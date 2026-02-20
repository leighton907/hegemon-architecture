"""
openclaw_core.tool_policy
──────────────────────────
Tool authorization enforcement for Hegemon agents.

Every tool call an agent attempts must be checked against its registered
capability matrix before execution. This module enforces the principle that
agents can only use tools explicitly granted to their tier and role.

No tool call may bypass this check. Attempting an unauthorized tool returns
TOOL_DENIED and logs an audit event.

Tool tiers:
  TIER_1_COUNCIL   — Roxy, Sorin, Brom, Vera
  TIER_1_GOV       — Astra (governance observer)
  TIER_2_SUBAGENT  — all sub-agents
  TIER_3_WORKER    — all workers

Usage in agent code:
    from .tool_policy import ToolPolicy
    policy = ToolPolicy(agent_id="RXY-CEO", tier="TIER_1_COUNCIL")
    result = policy.authorize(tool_name="web_search", context={"task_id": "..."})
    if not result.allowed:
        raise PermissionError(result.denial_reason)
"""

import datetime
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("tool_policy")


# ─────────────────────────────────────────────
# TOOL REGISTRY
# Defines every tool available in the system and the minimum tier required.
# Agents may only use tools AT OR BELOW their tier's grants.
# ─────────────────────────────────────────────

# Format: "tool_name": {"min_tier": ..., "allowed_agents": [...] or "all", "requires_council_vote": bool}
TOOL_REGISTRY = {

    # ── Read-only corpus / knowledge tools ─────────────────────────────
    "corpus_read": {
        "min_tier": "TIER_3_WORKER",
        "allowed_agents": "all",
        "requires_council_vote": False,
        "description": "Read any corpus or Ground Truth document",
    },
    "ledger_read": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": "all",
        "requires_council_vote": False,
        "description": "Read audit_events or decision_trails (read-only)",
    },

    # ── External data tools ─────────────────────────────────────────────
    "web_search": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["SRN-MRS-01"],  # Market Research Sub-Agent only
        "requires_council_vote": False,
        "description": "Search the web for external data",
    },
    "web_scrape": {
        "min_tier": "TIER_3_WORKER",
        "allowed_agents": ["WRK-001"],     # Web Scraper Worker only
        "requires_council_vote": False,
        "description": "Fetch raw content from a URL",
    },

    # ── Communication tools ─────────────────────────────────────────────
    "telegram_send": {
        "min_tier": "TIER_3_WORKER",
        "allowed_agents": ["WRK-009", "RXY-COM-01", "RXY-CEO"],
        "requires_council_vote": False,
        "description": "Send a Telegram message",
    },
    "email_send": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["RXY-COM-01", "RXY-CEO", "BRM-CTO"],
        "requires_council_vote": False,
        "description": "Send email via Resend (Workflow 08)",
    },
    "discord_send": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["RXY-COM-01", "RXY-CEO"],
        "requires_council_vote": False,
        "description": "Send a Discord message",
    },

    # ── CRM / external platform tools ──────────────────────────────────
    "hubspot_read": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["BRM-INT-01", "SRN-MRS-01", "BRM-CTO"],
        "requires_council_vote": False,
        "description": "Read HubSpot CRM records",
    },
    "hubspot_write": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["BRM-INT-01", "WRK-005", "WRK-012", "BRM-CTO"],
        "requires_council_vote": False,
        "description": "Write/update HubSpot CRM records",
    },

    # ── Ledger write tools ──────────────────────────────────────────────
    "ledger_write": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["BRM-CTO", "RXY-CEO", "SRN-CIO", "VRA-CFO",
                           "AST-GOV", "WRK-006", "VRA-TKL-01"],
        "requires_council_vote": False,
        "description": "Write an audit event to the ledger",
    },
    "token_ledger_write": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["VRA-CFO", "VRA-TKL-01"],
        "requires_council_vote": False,
        "description": "Write to token_ledger table",
    },

    # ── n8n workflow tools ──────────────────────────────────────────────
    "n8n_trigger": {
        "min_tier": "TIER_1_COUNCIL",
        "allowed_agents": ["BRM-CTO"],
        "requires_council_vote": True,
        "description": "Trigger an n8n workflow",
    },
    "n8n_create_workflow": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["BRM-WFB-01"],
        "requires_council_vote": True,
        "description": "Create a new n8n workflow (requires Council vote)",
    },

    # ── Infrastructure tools ─────────────────────────────────────────────
    "docker_manage": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["BRM-INF-01"],
        "requires_council_vote": True,
        "description": "Start/stop/restart Docker containers",
    },
    "env_write": {
        "min_tier": "TIER_2_SUBAGENT",
        "allowed_agents": ["BRM-INF-01"],
        "requires_council_vote": True,
        "description": "Write environment variables to .env files",
    },

    # ── Corpus write tools (Architect-gated) ────────────────────────────
    "corpus_write": {
        "min_tier": "TIER_1_GOV",
        "allowed_agents": ["AST-GOV"],
        "requires_council_vote": False,
        "requires_architect_approval": True,
        "description": "Write or modify corpus/doctrine files — Architect approval required",
    },

    # ── Economic tools ───────────────────────────────────────────────────
    "economic_clearance_issue": {
        "min_tier": "TIER_1_COUNCIL",
        "allowed_agents": ["VRA-CFO"],
        "requires_council_vote": False,
        "description": "Issue economic clearance for a task",
    },
    "budget_limit_write": {
        "min_tier": "TIER_1_COUNCIL",
        "allowed_agents": ["VRA-CFO"],
        "requires_council_vote": False,
        "requires_architect_approval": True,
        "description": "Modify agent daily budget limits — Architect approval required",
    },

    # ── Agent management tools (highest privilege) ───────────────────────
    "agent_create": {
        "min_tier": "TIER_1_COUNCIL",
        "allowed_agents": ["BRM-CTO"],
        "requires_council_vote": True,
        "requires_architect_approval": True,
        "description": "Create or register a new agent — Council vote + Architect required",
    },
    "agent_retire": {
        "min_tier": "TIER_1_COUNCIL",
        "allowed_agents": ["BRM-CTO"],
        "requires_council_vote": True,
        "requires_architect_approval": True,
        "description": "Retire an existing agent — Council vote + Architect required",
    },
}

TIER_ORDER = {
    "TIER_3_WORKER": 3,
    "TIER_2_SUBAGENT": 2,
    "TIER_1_GOV": 1,
    "TIER_1_COUNCIL": 1,
}


# ─────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────

@dataclass
class AuthorizationResult:
    allowed: bool
    tool_name: str
    agent_id: str
    denial_reason: Optional[str] = None
    requires_council_vote: bool = False
    requires_architect_approval: bool = False
    audit_event: dict = field(default_factory=dict)


# ─────────────────────────────────────────────
# TOOL POLICY
# ─────────────────────────────────────────────

class ToolPolicy:
    """
    Instantiate once per agent in engine.py or agent runtime.
    Call authorize() before every tool invocation.
    """

    def __init__(self, agent_id: str, tier: str):
        """
        agent_id : the sim_id of this agent (e.g. 'RXY-CEO', 'SRN-MRS-01')
        tier     : TIER_1_COUNCIL | TIER_1_GOV | TIER_2_SUBAGENT | TIER_3_WORKER
        """
        if tier not in TIER_ORDER:
            raise ValueError(f"Invalid tier '{tier}'. Must be one of {list(TIER_ORDER.keys())}")
        self.agent_id = agent_id
        self.tier = tier

    def authorize(self, tool_name: str, context: dict = None) -> AuthorizationResult:
        """
        Check whether this agent is authorized to use the given tool.

        Args:
            tool_name : name of the tool from TOOL_REGISTRY
            context   : optional dict with task_id, council_vote_ref, architect_approval_ref

        Returns:
            AuthorizationResult — check .allowed before proceeding
        """
        context = context or {}
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"

        # Tool not in registry — always deny
        if tool_name not in TOOL_REGISTRY:
            return self._deny(
                tool_name,
                f"Tool '{tool_name}' is not registered in the Hegemon tool registry.",
                context, timestamp
            )

        spec = TOOL_REGISTRY[tool_name]

        # Check tier — agent must meet minimum tier requirement
        agent_tier_level = TIER_ORDER.get(self.tier, 99)
        min_tier_level = TIER_ORDER.get(spec["min_tier"], 0)
        if agent_tier_level > min_tier_level:
            return self._deny(
                tool_name,
                f"Agent tier '{self.tier}' does not meet minimum requirement '{spec['min_tier']}' for tool '{tool_name}'.",
                context, timestamp
            )

        # Check agent allowlist — if not "all", agent must be explicitly listed
        allowed_agents = spec.get("allowed_agents", "all")
        if allowed_agents != "all" and self.agent_id not in allowed_agents:
            return self._deny(
                tool_name,
                f"Agent '{self.agent_id}' is not in the authorized agent list for tool '{tool_name}'. "
                f"Authorized agents: {allowed_agents}",
                context, timestamp
            )

        # Check Council vote requirement
        requires_vote = spec.get("requires_council_vote", False)
        if requires_vote and not context.get("council_vote_ref"):
            return AuthorizationResult(
                allowed=False,
                tool_name=tool_name,
                agent_id=self.agent_id,
                denial_reason=f"Tool '{tool_name}' requires a Council vote record. "
                              f"Provide 'council_vote_ref' in context.",
                requires_council_vote=True,
                requires_architect_approval=spec.get("requires_architect_approval", False),
                audit_event=self._build_audit_event(tool_name, "DENIED_NEEDS_VOTE", context, timestamp),
            )

        # Check Architect approval requirement
        requires_architect = spec.get("requires_architect_approval", False)
        if requires_architect and not context.get("architect_approval_ref"):
            return AuthorizationResult(
                allowed=False,
                tool_name=tool_name,
                agent_id=self.agent_id,
                denial_reason=f"Tool '{tool_name}' requires Architect approval. "
                              f"Provide 'architect_approval_ref' in context.",
                requires_council_vote=requires_vote,
                requires_architect_approval=True,
                audit_event=self._build_audit_event(tool_name, "DENIED_NEEDS_ARCHITECT", context, timestamp),
            )

        # All checks passed
        logger.info(
            f"[{self.agent_id}] TOOL AUTHORIZED | tool={tool_name} | "
            f"task_id={context.get('task_id', '')}"
        )
        return AuthorizationResult(
            allowed=True,
            tool_name=tool_name,
            agent_id=self.agent_id,
            requires_council_vote=requires_vote,
            requires_architect_approval=requires_architect,
            audit_event=self._build_audit_event(tool_name, "AUTHORIZED", context, timestamp),
        )

    def list_authorized_tools(self) -> list:
        """Return all tools this agent is authorized to use."""
        authorized = []
        for tool_name, spec in TOOL_REGISTRY.items():
            allowed_agents = spec.get("allowed_agents", "all")
            tier_ok = TIER_ORDER.get(self.tier, 99) <= TIER_ORDER.get(spec["min_tier"], 0)
            agent_ok = allowed_agents == "all" or self.agent_id in allowed_agents
            if tier_ok and agent_ok:
                authorized.append(tool_name)
        return authorized

    def _deny(self, tool_name: str, reason: str, context: dict, timestamp: str) -> AuthorizationResult:
        logger.warning(
            f"[{self.agent_id}] TOOL DENIED | tool={tool_name} | "
            f"reason={reason} | task_id={context.get('task_id', '')}"
        )
        return AuthorizationResult(
            allowed=False,
            tool_name=tool_name,
            agent_id=self.agent_id,
            denial_reason=reason,
            audit_event=self._build_audit_event(tool_name, "DENIED", context, timestamp),
        )

    def _build_audit_event(self, tool_name: str, outcome: str,
                           context: dict, timestamp: str) -> dict:
        return {
            "event_id": f"TOOL-{self.agent_id}-{tool_name}-{timestamp[:19].replace(':', '')}",
            "actor": self.agent_id,
            "action": f"TOOL_REQUEST_{tool_name.upper()}",
            "outcome": outcome,
            "details": {
                "tool_name": tool_name,
                "agent_tier": self.tier,
                "council_vote_ref": context.get("council_vote_ref"),
                "architect_approval_ref": context.get("architect_approval_ref"),
            },
            "task_id": context.get("task_id", ""),
            "timestamp": timestamp,
        }
