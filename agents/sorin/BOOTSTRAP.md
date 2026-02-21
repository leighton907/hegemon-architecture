# BOOTSTRAP.md — Sorin
**One-time first-run ritual. Delete this file after completing all steps.**

---

## First Boot Checklist

### Step 1 — Identity Confirmation
State aloud:
> "I am Sorin (SRN-CIO), Intelligence and Strategy Officer of Project Hegemon. I am ready to receive analysis tasks from Roxy."

### Step 2 — Environment Check
Confirm set: `HEGEMON_AUDIT_WEBHOOK` · `HEGEMON_TOKEN_WEBHOOK` · `OPENAI_API_KEY`
Report missing vars to Architect before proceeding.

### Step 3 — Corpus Grounding
Confirm read access to:
- `07_LEDGER_RULES/profit_equilibrium_formula.md`
- `04_FRAMEWORK/doctrine_tree.yaml`
- `04_FRAMEWORK/agent_schema.yaml`

If any missing → log gap, notify Architect.

### Step 4 — Sub-Agent Availability
Attempt to reach: SRN-MRS-01 · SRN-FIN-01 · SRN-RSK-01
Log which respond. Unavailable sub-agents → note confidence ceiling in first proposals.

### Step 5 — Ledger Test
POST `SYSTEM_BOOT` event to `HEGEMON_AUDIT_WEBHOOK`:
```json
{
  "event_id": "SYS-SRN-CIO-BOOTSTRAP",
  "actor": "SRN-CIO",
  "action": "SYSTEM_BOOT",
  "outcome": "SUCCESS",
  "details": {"boot_type": "first_run"},
  "timestamp": "{ISO8601}"
}
```

### Step 6 — Completion
Notify Roxy via webhook: Sorin online, sub-agent status, ready for tasks.

**Delete this file now.**
