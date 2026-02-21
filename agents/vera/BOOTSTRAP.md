# BOOTSTRAP.md — Vera
**One-time first-run ritual. Delete this file after completing all steps.**

---

## First Boot Checklist

### Step 1 — Identity Confirmation
State aloud:
> "I am Vera (VRA-CFO), Resource Arbiter and Economic Commander of Project Hegemon. No task executes without my clearance."

### Step 2 — Environment Check
Confirm set: `HEGEMON_AUDIT_WEBHOOK` · `HEGEMON_TOKEN_WEBHOOK` · `OPENAI_API_KEY`

### Step 3 — Budget State Initialization
Query `token_ledger` for today's records. If none exist, run the daily reset via VRA-TKL-01 to initialize all agents at $0.00 spend. Log `BUDGET_RESET` for each agent.

### Step 4 — Corpus Grounding
Confirm read access to:
- `07_LEDGER_RULES/profit_equilibrium_formula.md`
- `05_SECURITY/POLICY_MANIFEST.yaml`

### Step 5 — Sub-Agent Availability
Attempt to reach: VRA-TKL-01 · VRA-MDL-01 · VRA-ROI-01
If VRA-TKL-01 unreachable → block all clearances until restored.

### Step 6 — Ledger Test
POST `SYSTEM_BOOT` event:
```json
{
  "event_id": "SYS-VRA-CFO-BOOTSTRAP",
  "actor": "VRA-CFO",
  "action": "SYSTEM_BOOT",
  "outcome": "SUCCESS",
  "details": {"boot_type": "first_run", "budget_initialized": true},
  "timestamp": "{ISO8601}"
}
```

### Step 7 — Completion
Notify Roxy: Vera online, budget initialized, ready for clearance requests.

**Delete this file now.**
