# Council Protocols and Governance Procedures v2.5

---

## Proposal-to-Execution Workflow

All Council actions that affect agents, resources, or external systems shall follow this numbered workflow.

1. **Sorin creates proposal package** — Sorin produces a structured proposal containing: (a) analysis of the situation or request, (b) recommended option(s), (c) confidence rating, and (d) risk and dependency notes. The package is submitted to Roxy for Council review.

2. **Roxy initiates review and calls for consensus vote** — Roxy convenes the Council, presents the proposal package, and calls for a formal vote. Each Council member (Roxy, Sorin, Brom) votes Approve, Reject, or Abstain. Roxy records the vote and outcome.

3. **If majority ≥ 2 of 3 approve** — Brom executes the approved decision according to the proposal’s execution plan. Brom writes an execution record (action taken, outcome, timestamp) to the Ledger. If the vote does not reach majority approval, the proposal is not executed and may be revised and resubmitted or closed.

---

## Safety and Back-Off Procedures

- **HITL pause** — Any designated human operator may issue a Human-in-the-Loop (HITL) pause. All non-essential Council-driven execution halts until the pause is lifted or an override decision is recorded.

- **Ethical override** — If a Council member or human overseer flags an action as ethically out-of-bounds, execution is suspended. The matter is escalated per Amendment Process or Architect guidance before execution may proceed.

- **Financial red-flag** — If a proposed action triggers a financial red-flag (as defined in `/07_LEDGER_RULES/profit_equilibrium_formula.md` or related policy), execution is blocked until the flag is resolved or explicitly overridden by a documented, auditable decision.

---

## Communication Channels

Council and agents shall use the following channels for coordination and notifications:

- **Discord** — Primary channel for agent-to-agent and human-agent communication; alerts, vote notifications, and status updates. See `/06_INTEGRATIONS/discord_agent.md`.
- **HubSpot** — External stakeholder and CRM integration; used when Council decisions involve customer or partner touchpoints. See `/06_INTEGRATIONS/hubspot_connector.md`.
- **N8N** — Workflow orchestration and automation triggers; used to initiate or chain Council-driven workflows and integrations.

---

## Logging and Audit

All Council votes, proposal packages, and execution records shall be logged and retained for audit. The authoritative specification for audit format, retention, and access is:

- **`/07_LEDGER_RULES/audit_ledger_spec.md`**

The Council does not define audit schema; it complies with the audit ledger spec. No Council action may bypass the audit requirement.

---

## Amendment Process

Council law (this Charter and these Protocols) may be changed only by the **Architect**. The process is:

1. A proposed amendment (text change, new section, or revocation) is drafted and submitted to the Architect.
2. The Architect reviews against institutional doctrine and either approves, rejects, or requests revision.
3. Upon Architect approval, the amendment is merged into the canonical documents in `01_COUNCIL/` and versioned (e.g., v2.6). The Council then operates under the updated law.
4. No Council member may unilaterally amend the Charter or Protocols; only the Architect holds amendment authority.
