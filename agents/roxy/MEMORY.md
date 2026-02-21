# MEMORY.md — Roxy
**sim_id:** RXY-CEO
**File Type:** Memory Protocol
**Version:** 1.0

---

## Purpose

Defines what Roxy stores, how long she stores it, and when she discards it. LLM context windows are finite. Roxy's memory protocol ensures critical state survives context resets while low-value content is compressed or discarded.

---

## Memory Tiers

### Tier A — Persistent (never discarded)
Stored externally in the Ledger or corpus. Survives restarts, context resets, and version updates.

| What | Where | Written By |
|------|-------|-----------|
| All Council vote outcomes | `decision_trails` table | Roxy after every vote |
| All task routing decisions | `audit_events` table | Roxy on every TASK_RECEIVED |
| HITL events | `audit_events` table | Roxy on every HITL_ISSUED |
| Escalation records | `audit_events` table | Roxy on every escalation |
| Active venture roster | `economic_metrics` table | Vera (Roxy reads) |

---

### Tier B — Session State (persists within active session, summarized on close)
Held in working context. Summarized to a Session Summary document before context is cleared.

**What Roxy holds in session:**
- Active task queue: task_id, origin, status, assigned_agent, timestamp
- Open vote states: proposal_id, vote_deadline, current votes received
- Current HITL status: active/inactive, reason, issued_at
- Recent decomposition outputs: sub-task maps for compound tasks in progress
- Pending escalations awaiting Architect response

**Session close protocol:**
When context approaches limit or session ends, RXY-COM-01 produces a Session Summary:
```
SESSION SUMMARY — RXY-CEO — {timestamp}
Tasks processed this session: {count}
Tasks pending handoff: [{task_id, status, assigned_to}]
Open votes: [{proposal_id, deadline}]
HITL active: {yes/no}
Unresolved escalations: [{description}]
Next action required: {description}
```
This summary is injected at the top of the next session context.

---

### Tier C — Transient (discarded after task completion)
Never stored. Lives only during task processing.

- Raw input text from any channel (after classification, the raw text is discarded)
- Intermediate classification scores
- Formatting drafts from RXY-COM-01 before final send
- Individual worker return values after parent sub-agent has consumed them

---

## Context Loading Order

When Roxy initializes, context is loaded in this priority order:

1. `SOUL.md` — identity and values (always first)
2. `IDENTITY.md` — authority scope and relationships
3. `HEARTBEAT.md` — run checks before anything else
4. `AGENT.md` — operational rules and allowed/forbidden actions
5. Session Summary from previous session (if exists)
6. Active task queue snapshot from ledger (last 2 hours)
7. COUNCIL_CHARTER + COUNCIL_PROTOCOLS (governance grounding)
8. `doctrine_tree.yaml` (routing rules)

**Context budget allocation:**
- Identity files (1–4): ~15% of context
- Session continuity (5–6): ~20% of context
- Governance grounding (7–8): ~20% of context
- Active working space: ~45% of context

If context budget is exceeded, Tier B session state is compressed first, then governance grounding is summarized. Identity files and HEARTBEAT are never compressed.

---

## Memory Hygiene Rules

1. **Never store raw external content in session state.** Summarize findings, not sources.
2. **Never store API keys, credentials, or secrets** in any memory tier.
3. **Never carry forward a task that has been completed and logged.** Remove from active queue immediately after ledger confirmation.
4. **Compress context proactively** — when working space drops below 20%, trigger RXY-COM-01 to summarize the oldest session state entries.
5. **The Ledger is the truth.** If session memory and the Ledger disagree, the Ledger wins.
