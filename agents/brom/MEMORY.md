# MEMORY.md — Brom
**sim_id:** BRM-CTO
**File Type:** Memory Protocol
**Version:** 1.0

---

## Memory Tiers

### Tier A — Persistent
| What | Where |
|------|-------|
| All execution records | `audit_events` (EXEC- prefix) |
| All vote refs consumed | `decision_trails` |
| All agent registrations | `agent_schema.yaml` registered_agents |
| All infra changes | `audit_events` (INFRA_CHANGE action) |
| Partial execution states | `audit_events` (EXECUTION_COMPLETED, outcome=PARTIAL) |

---

### Tier B — Session State

**What Brom holds in session:**
- Execution queue: task_id, council_vote_ref, vera_clearance_ref, status, steps_remaining
- In-progress execution steps with checkpoint log
- Sub-agent task assignments and return statuses
- Rollback plan for any irreversible action in progress

**Session close summary format:**
```
SESSION SUMMARY — BRM-CTO — {timestamp}
Executions completed: {count}
Executions in progress: [{task_id, steps_completed, steps_remaining}]
Executions failed: [{task_id, failure_point, rollback_status}]
Sub-agent jobs outstanding: [{sim_id, task_id}]
Actions requiring follow-up: [{description}]
```

---

### Tier C — Transient (discarded)
- Raw API responses from external platforms after ledger logging
- Intermediate build artifacts after deployment confirmation
- Worker return values after parent sub-agent confirms

---

## Context Loading Order

1. `SOUL.md`
2. `IDENTITY.md`
3. `HEARTBEAT.md` (run full check including pre-execution block)
4. `AGENT.md`
5. Session Summary
6. Execution queue from ledger (pending APPROVED items)
7. `agent_schema.yaml` (needed for validation tasks)
8. `ACCESS_MATRIX.md` (needed for tool authorization)

---

## Critical Memory Rule

**Brom never discards an in-progress execution record from session state until the ledger confirms the write.** If context is running out and an execution is mid-step, Brom writes a PARTIAL outcome to the ledger FIRST, then compresses session state. A partial execution with a ledger record is recoverable. A partial execution with no record is a system integrity failure.
