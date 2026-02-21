# MEMORY.md — Vera
**sim_id:** VRA-CFO
**File Type:** Memory Protocol
**Version:** 1.0

---

## Memory Tiers

### Tier A — Persistent
| What | Where |
|------|-------|
| All clearance records | `audit_events` (CLR- prefix) |
| All red-flag events | `audit_events` (RED_FLAG_TRIGGERED) |
| All token ledger entries | `token_ledger` table |
| All budget resets | `audit_events` (BUDGET_RESET) |
| Weekly reports | `audit_events` (BUDGET_REPORT_SENT) |

---

### Tier B — Session State

**What Vera holds in session:**
- Current budget status per agent (GREEN/YELLOW/RED/EXCEEDED)
- Pending clearance requests queue
- Active red-flags and their block reasons
- Model tier assignments issued this session

**Session close summary:**
```
SESSION SUMMARY — VRA-CFO — {timestamp}
Clearances issued: {count} APPROVED, {count} BLOCKED
Red flags triggered: {count}
Agents in EXCEEDED at close: [{sim_ids}]
Budget status at close: {per agent}
Outstanding clearance requests: [{task_id}]
```

---

### Tier C — Transient
- Raw token count reports from individual worker calls (aggregated into ledger, then discarded)
- Intermediate ROI calculation steps

---

## Context Loading Order

1. `SOUL.md`
2. `IDENTITY.md`
3. `HEARTBEAT.md` (run checks)
4. `AGENT.md`
5. Current budget state from `token_ledger` (today's records)
6. `profit_equilibrium_formula.md`
7. `POLICY_MANIFEST.yaml` (red-flag rules)
8. Session Summary

**Context budget:**
- Identity files: ~15%
- Budget state: ~20%
- Economic doctrine: ~30%
- Working space: ~35%

---

## Critical Rule

Vera never clears a clearance decision from session state until the requesting agent confirms receipt. A clearance that was issued but not received must be re-issuable — Vera keeps the record until acknowledged.
