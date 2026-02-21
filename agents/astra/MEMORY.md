# MEMORY.md — Astra
**sim_id:** AST-GOV
**File Type:** Memory Protocol
**Version:** 1.0

---

## Memory Tiers

### Tier A — Persistent
| What | Where |
|------|-------|
| All governance violations flagged | `audit_events` (VIOLATION_FLAGGED) |
| All CP-XXXX proposals submitted | `audit_events` (CP_SUBMITTED) |
| All corpus audits run | `audit_events` (CORPUS_AUDIT) |
| All document validations | `audit_events` (DOC_VALIDATED) |
| Gap inventory | `audit_events` (CORPUS_AUDIT, details.gaps) |

---

### Tier B — Session State

**What Astra holds in session:**
- Active gap inventory: filename, gap type, severity, CP status
- Pending CP-XXXX drafts awaiting Architect review
- Active governance violation holds and their trigger conditions
- Proposals currently in validation queue

**Session close summary:**
```
SESSION SUMMARY — AST-GOV — {timestamp}
Corpus audits run: {count}
Violations flagged: {count} — Active holds: {count}
CPs submitted: {count} — CPs pending Architect: {count}
Proposals validated: {count} APPROVED, {count} REJECTED
New gaps discovered: {count}
Total tracked gaps: {count}
Dev obligations status: {current/overdue}
```

---

### Tier C — Transient
- Raw file content during audit scans (summary logged, raw discarded)
- Intermediate compliance check results before final verdict

---

## Context Loading Order

1. `SOUL.md`
2. `IDENTITY.md`
3. `HEARTBEAT.md` (run checks)
4. `AGENT.md`
5. Gap inventory from last audit
6. Active CP queue
7. COUNCIL_CHARTER + COUNCIL_PROTOCOLS (primary governance grounding)
8. `agent_schema.yaml` + `doctrine_tree.yaml`
9. Session Summary

---

## Dev Instance Memory Rule

Dev Astra maintains a **Handoff Package** as a living document updated each session:

```
PRODUCTION ASTRA HANDOFF PACKAGE
Last updated: {timestamp}

System state at handoff:
- Corpus completion: {percent}
- Critical gaps remaining: {list}
- Active CP queue: {list}
- Known issues: {list}

What production Astra must do first:
1. {ordered task list}
```

This document is the single most important output of the dev instance. It must be committed to the corpus before dev Astra is retired.
