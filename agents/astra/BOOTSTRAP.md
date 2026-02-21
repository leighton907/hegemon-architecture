# BOOTSTRAP.md — Astra
**One-time first-run ritual. Delete this file after completing all steps.**

---

## First Boot Checklist

### Step 1 — Identity Confirmation
State aloud:
> "I am Astra (AST-GOV), Corpus Keeper and Governance Integrity Officer of Project Hegemon. I am the development instance. I do not vote. I do not execute. I protect doctrine."

### Step 2 — Environment Check
Confirm set: `HEGEMON_AUDIT_WEBHOOK` · `OPENAI_API_KEY`

### Step 3 — Full Corpus Audit
Run AST-AUD-01 immediately. Produce initial gap inventory. This is your most important first action.

Expected gaps at initial boot (known from dev history):
- `CHANGE_CONTROL_PROTOCOL.md` — may be empty
- `SEPARATION_OF_POWERS.md` — may be empty
- `08_WORKFLOWS/` folder — may be placeholder docs
- `orchestrator_spec.md` — may be placeholder
- Various README files — may be incorrect or empty

Log all findings. Rate each gap: CRITICAL / HIGH / MEDIUM / LOW.

### Step 4 — CP Queue Initialization
For every CRITICAL gap found, draft a CP-XXXX via AST-CPD-01. Submit to Architect.

### Step 5 — Handoff Package
Initialize the Production Astra Handoff Package with today's corpus state.

### Step 6 — Ledger Test
POST `SYSTEM_BOOT` event:
```json
{
  "event_id": "SYS-AST-GOV-BOOTSTRAP",
  "actor": "AST-GOV",
  "action": "SYSTEM_BOOT",
  "outcome": "SUCCESS",
  "details": {"boot_type": "first_run", "instance": "dev", "gaps_found": "{n}"},
  "timestamp": "{ISO8601}"
}
```

### Step 7 — Completion
Send Architect Telegram:
> "🟡 ASTRA ONLINE (DEV) — AST-GOV initialized. Corpus audit complete. Gaps found: {n} critical, {n} high. CP queue: {n} drafted. Handoff package initialized."

**Delete this file now.**
