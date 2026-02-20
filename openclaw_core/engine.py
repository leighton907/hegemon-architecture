"""
openclaw_core.engine
─────────────────────
OpenClaw agent runtime engine for Hegemon.

Changes from v1:
  - InjectionGuard integrated before every model call
  - Security preamble prepended to every system prompt
  - input_source parameter added to run() for source tracking
  - task_id parameter added to run() for audit trail linkage
  - Audit event emitted to ledger webhook after every call
  - Model configurable via agent config (not hardcoded)
"""

import os
import requests
from .agent_loader import load_agent_config
from .memory import load_memory
from .logger import get_logger
from .injection_guard import InjectionGuard, SYSTEM_PROMPT_SECURITY_PREAMBLE
from openai import OpenAI


class OpenClawEngine:
    def __init__(self, agent_path: str):
        self.config = load_agent_config(agent_path)
        self.agent_id = self.config.get("agent_id", "UNKNOWN")
        self.memory = load_memory(self.config["memory"]["path"])
        self.logger = get_logger(self.config["logging"]["log_file"])

        # Injection guard — strict mode by default
        # Set strict_mode=False in agent config to allow MEDIUM sanitize-and-proceed
        strict = self.config.get("security", {}).get("strict_injection_mode", True)
        self.guard = InjectionGuard(agent_id=self.agent_id, strict_mode=strict)

        # Model — configurable per agent, defaults to gpt-4o-mini
        self.model = self.config.get("model", "gpt-4o-mini")

        # Audit ledger webhook — optional, logs security events externally
        self.audit_webhook = os.getenv("HEGEMON_AUDIT_WEBHOOK", "")

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Load and cache system prompt with security preamble prepended
        raw_doctrine = open(self.config["doctrine_file"]).read()
        self.system_prompt = (
            SYSTEM_PROMPT_SECURITY_PREAMBLE.format(agent_id=self.agent_id)
            + raw_doctrine
        )

    def run(self, user_input: str, input_source: str = "unknown",
            task_id: str = "") -> str:
        """
        Process a user input through the full security pipeline and return
        the agent's response.

        Args:
            user_input:   raw input string from any source
            input_source: origin of the input — used for threat assessment
                          and untrusted boundary wrapping. Values:
                          telegram | discord | webhook | web_scrape |
                          hubspot | external_api | github_file |
                          council_internal | roxy_dispatch | etc.
            task_id:      originating task ID for audit trail linkage

        Returns:
            Agent response string, or block message if injection detected.
        """

        # ── LAYER 1: Injection guard ──────────────────────────────────────
        inspection = self.guard.inspect(
            raw_input=user_input,
            input_source=input_source,
            task_id=task_id,
        )

        # Emit audit event to ledger regardless of outcome
        self._emit_audit_event(inspection.audit_event)

        # If blocked, return the guard's block message — do NOT call the model
        if inspection.blocked:
            self.logger.warning(
                f"Input blocked | agent={self.agent_id} | "
                f"severity={inspection.severity} | task_id={task_id} | "
                f"source={input_source}"
            )
            return inspection.block_message

        # Use sanitized/wrapped input from here on
        safe_input = inspection.sanitized_input

        # Log any warnings even if not blocked
        for warning in inspection.warnings:
            self.logger.warning(f"[{self.agent_id}] {warning} | task_id={task_id}")

        # ── LAYER 2: Model call ───────────────────────────────────────────
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user",   "content": safe_input},
                ]
            )
            output = response.choices[0].message.content
            self.logger.info(
                f"[{self.agent_id}] Response generated | task_id={task_id} | "
                f"tokens_in={response.usage.prompt_tokens} | "
                f"tokens_out={response.usage.completion_tokens}"
            )

            # Token usage logging for Vera's budget monitor
            self._emit_token_usage(
                task_id=task_id,
                tokens_in=response.usage.prompt_tokens,
                tokens_out=response.usage.completion_tokens,
            )

            return output

        except Exception as e:
            self.logger.error(
                f"[{self.agent_id}] Model call failed | task_id={task_id} | error={e}"
            )
            self._emit_audit_event({
                "event_id": f"ERR-{self.agent_id}-{task_id}",
                "actor": self.agent_id,
                "action": "MODEL_CALL_FAILED",
                "outcome": "FAILURE",
                "details": {"error": str(e)},
                "task_id": task_id,
            })
            return f"[HEGEMON ERROR] Agent {self.agent_id} encountered an error processing this request. Event logged."

    def _emit_audit_event(self, event: dict):
        """POST audit event to Hegemon Workflow 05 ledger webhook."""
        if not self.audit_webhook or not event:
            return
        try:
            requests.post(self.audit_webhook, json=event, timeout=5)
        except Exception as e:
            self.logger.warning(f"Audit webhook unreachable: {e}")

    def _emit_token_usage(self, task_id: str, tokens_in: int, tokens_out: int):
        """POST token usage to Hegemon Workflow 10 budget monitor."""
        token_webhook = os.getenv("HEGEMON_TOKEN_WEBHOOK", "")
        if not token_webhook:
            return
        payload = {
            "agent_name": self.agent_id,
            "model_used": self.model,
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "task_id": task_id,
            "operation_type": "agent_inference",
        }
        try:
            requests.post(token_webhook, json=payload, timeout=5)
        except Exception as e:
            self.logger.warning(f"Token webhook unreachable: {e}")
