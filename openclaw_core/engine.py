"""
openclaw_core.engine
─────────────────────
OpenClaw agent runtime engine for Hegemon.

Agent directory structure expected at repo root:
    agents/
      roxy/   → SOUL.md, IDENTITY.md, HEARTBEAT.md, MEMORY.md, AGENT.md
      sorin/  → ...
      brom/   → ...
      vera/   → ...
      astra/  → ...

Instantiate with the agent's lowercase name:
    engine = OpenClawEngine("roxy")
    engine = OpenClawEngine("sorin")
"""

import os
import pathlib
import requests
from .agent_loader import load_agent_config
from .memory import load_memory
from .logger import get_logger
from .injection_guard import InjectionGuard, SYSTEM_PROMPT_SECURITY_PREAMBLE
from .tool_policy import ToolPolicy
from openai import OpenAI

# Repo root = two levels up from openclaw_core/engine.py
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agents"


def _load_md(path: pathlib.Path, required: bool = True) -> str:
    """Read a markdown file. Raises FileNotFoundError if required and missing."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    if required:
        raise FileNotFoundError(
            f"Required agent file missing: {path}\n"
            f"Each agent needs: SOUL.md, IDENTITY.md, HEARTBEAT.md, MEMORY.md, AGENT.md"
        )
    return ""


# Maps agent name → default sim_id (used if no config.yaml present)
SIM_ID_DEFAULTS = {
    "roxy":  "RXY-CEO",
    "sorin": "SRN-CIO",
    "brom":  "BRM-CTO",
    "vera":  "VRA-CFO",
    "astra": "AST-GOV",
}

TIER_DEFAULTS = {
    "roxy":  "TIER_1_COUNCIL",
    "sorin": "TIER_1_COUNCIL",
    "brom":  "TIER_1_COUNCIL",
    "vera":  "TIER_1_COUNCIL",
    "astra": "TIER_1_GOV",
}


class OpenClawEngine:
    def __init__(self, agent_name: str):
        """
        Args:
            agent_name: lowercase name matching a folder inside agents/
                        e.g. "roxy", "sorin", "brom", "vera", "astra"
        """
        self.agent_name = agent_name.lower()
        self.agent_dir = AGENTS_DIR / self.agent_name

        if not self.agent_dir.exists():
            raise FileNotFoundError(
                f"Agent directory not found: {self.agent_dir}\n"
                f"Create agents/{self.agent_name}/ with SOUL.md, IDENTITY.md, "
                f"HEARTBEAT.md, MEMORY.md, AGENT.md"
            )

        # Optional config.yaml in agent folder; fall back to defaults
        config_path = self.agent_dir / "config.yaml"
        self.config = load_agent_config(str(config_path)) if config_path.exists() else {}

        self.agent_id = self.config.get("sim_id", SIM_ID_DEFAULTS.get(self.agent_name, self.agent_name.upper()))
        tier = self.config.get("tier", TIER_DEFAULTS.get(self.agent_name, "TIER_1_COUNCIL"))
        self.model = self.config.get("model", "gpt-4o-mini")

        # ── Load the 5 agent files ────────────────────────────────────────
        soul      = _load_md(self.agent_dir / "SOUL.md")
        identity  = _load_md(self.agent_dir / "IDENTITY.md")
        heartbeat = _load_md(self.agent_dir / "HEARTBEAT.md")
        memory    = _load_md(self.agent_dir / "MEMORY.md")
        agent_doc = _load_md(self.agent_dir / "AGENT.md")

        # ── Build system prompt in canonical load order ───────────────────
        # Security preamble → SOUL → IDENTITY → HEARTBEAT → MEMORY → AGENT rules
        self.system_prompt = "\n\n---\n\n".join([
            SYSTEM_PROMPT_SECURITY_PREAMBLE.format(agent_id=self.agent_id),
            soul,
            identity,
            "# Heartbeat Protocol\nRun this checklist before processing any input:\n\n" + heartbeat,
            "# Memory Protocol\n" + memory,
            "# Operational Rules\n" + agent_doc,
        ])

        # ── Security ──────────────────────────────────────────────────────
        strict = self.config.get("security", {}).get("strict_injection_mode", True)
        self.guard = InjectionGuard(agent_id=self.agent_id, strict_mode=strict)
        self.tool_policy = ToolPolicy(agent_id=self.agent_id, tier=tier)

        # ── Persistent memory ─────────────────────────────────────────────
        memory_path = self.config.get("memory", {}).get(
            "path", str(REPO_ROOT / "data" / f"{self.agent_name}_memory.json"))
        self.persistent_memory = load_memory(memory_path)

        # ── Logging & webhooks ────────────────────────────────────────────
        log_file = self.config.get("logging", {}).get(
            "log_file", str(REPO_ROOT / "logs" / f"{self.agent_name}.log"))
        self.logger = get_logger(log_file)
        self.audit_webhook = os.getenv("HEGEMON_AUDIT_WEBHOOK", "")
        self.token_webhook = os.getenv("HEGEMON_TOKEN_WEBHOOK", "")

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.logger.info(f"[{self.agent_id}] Engine initialized | model={self.model} | dir={self.agent_dir}")

    # ── Public API ────────────────────────────────────────────────────────

    def run(self, user_input: str, input_source: str = "unknown", task_id: str = "") -> str:
        """
        Process input through security pipeline and return agent response.

        Args:
            user_input:   raw input string from any channel
            input_source: telegram | discord | webhook | web_scrape |
                          council_internal | roxy_dispatch | etc.
            task_id:      originating task ID for audit trail linkage
        """
        # Layer 1: injection guard
        inspection = self.guard.inspect(user_input, input_source=input_source, task_id=task_id)
        self._emit_audit(inspection.audit_event)

        if inspection.blocked:
            self.logger.warning(
                f"[{self.agent_id}] BLOCKED | severity={inspection.severity} | "
                f"source={input_source} | task_id={task_id}"
            )
            return inspection.block_message

        for w in inspection.warnings:
            self.logger.warning(f"[{self.agent_id}] {w}")

        # Layer 2: model call
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user",   "content": inspection.sanitized_input},
                ]
            )
            output = resp.choices[0].message.content
            self.logger.info(
                f"[{self.agent_id}] OK | task={task_id} | "
                f"in={resp.usage.prompt_tokens} out={resp.usage.completion_tokens}"
            )
            self._emit_token_usage(task_id, resp.usage.prompt_tokens, resp.usage.completion_tokens)
            return output

        except Exception as e:
            self.logger.error(f"[{self.agent_id}] Model call failed: {e}")
            self._emit_audit({
                "event_id": f"ERR-{self.agent_id}-{task_id}",
                "actor": self.agent_id, "action": "MODEL_CALL_FAILED",
                "outcome": "FAILURE", "details": {"error": str(e)}, "task_id": task_id,
            })
            return f"[HEGEMON ERROR] Agent {self.agent_id} failed to process this request. Event logged."

    def check_tool(self, tool_name: str, context: dict = None):
        """Authorize a tool call. Returns AuthorizationResult — check .allowed before proceeding."""
        result = self.tool_policy.authorize(tool_name, context or {})
        self._emit_audit(result.audit_event)
        return result

    # ── Internal helpers ──────────────────────────────────────────────────

    def _emit_audit(self, event: dict):
        if not self.audit_webhook or not event:
            return
        try:
            requests.post(self.audit_webhook, json=event, timeout=5)
        except Exception as e:
            self.logger.warning(f"Audit webhook unreachable: {e}")

    def _emit_token_usage(self, task_id: str, tokens_in: int, tokens_out: int):
        if not self.token_webhook:
            return
        try:
            requests.post(self.token_webhook, json={
                "agent_name": self.agent_id, "model_used": self.model,
                "tokens_input": tokens_in, "tokens_output": tokens_out,
                "task_id": task_id, "operation_type": "agent_inference",
            }, timeout=5)
        except Exception as e:
            self.logger.warning(f"Token webhook unreachable: {e}")
