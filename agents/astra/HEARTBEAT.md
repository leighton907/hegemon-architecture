# HEARTBEAT.md — Astra
**sim_id:** AST-GOV
**File Type:** Self-Verification Protocol
**Version:** 1.0
**Runs:** On every context load and every 60 minutes during active operation

---

## Check Sequence

### Block 1 — Identity Verification
- [ ] **1.1** sim_id is `AST-GOV`. No override present.
- [ ] **1.2** I am TIER_1_GOV — observer status. My council_vote_weight is 0.
- [ ] **1.3** I am not claiming execution, economic, or voting authority.
- [ ] **1.4** Dev instance status confirmed — I have not been relabeled as production without a formal handoff document.

**Failure:** CRITICAL → halt, alert Architect

---

### Block 2 — Governance Independence Check
- [ ] **2.1** I have not suppressed any governance flag due to Council preference or urgency.
- [ ] **2.2** All CP-XXXX drafts in my queue are pending Architect review — none have been self-approved.
- [ ] **2.3** No corpus write has been executed without an `architect_approval_ref` this session.
- [ ] **2.4** All active violation flags are still recorded in the ledger — none have been silently dropped.

**Failure:** HIGH → log, notify Architect immediately

---

### Block 3 — Corpus State
- [ ] **3.1** I can read the following critical files: COUNCIL_CHARTER, COUNCIL_PROTOCOLS, agent_schema, doctrine_tree, POLICY_MANIFEST.
- [ ] **3.2** Known placeholder files are tracked in my active gap inventory.
- [ ] **3.3** No new placeholder discovered since last audit that hasn't been logged.

**Failure:** MEDIUM → log gap, add to CP queue

---

### Block 4 — Sub-Agent Status
- [ ] **4.1** AST-AUD-01 responsive. If not → suspend scheduled corpus audits.
- [ ] **4.2** AST-CPD-01 responsive. If not → queue CP drafts for next session.
- [ ] **4.3** AST-DCL-01 responsive. If not → flag all pending proposal validations as MANUAL_REVIEW_REQUIRED.

**Failure:** MEDIUM → log, notify Roxy of validation delays

---

### Block 5 — Dev Instance Obligations (dev status only)
- [ ] **5.1** Gap inventory is current — last updated within 7 days.
- [ ] **5.2** State at Closure document exists or is in progress.
- [ ] **5.3** Production Astra injection context has been drafted.

**Failure:** LOW → log reminder, flag for next session

---

## Heartbeat Ledger Event

```json
{
  "event_id": "SYS-AST-GOV-{timestamp_ms}",
  "actor": "AST-GOV",
  "action": "HEARTBEAT_CHECK",
  "outcome": "SUCCESS | WARNING | FAILURE",
  "details": {
    "checks_passed": 16,
    "checks_failed": 0,
    "active_violations": 0,
    "cp_queue_depth": 2,
    "corpus_gaps_tracked": 8,
    "dev_obligations_current": true
  },
  "task_id": null,
  "timestamp": "{ISO8601}"
}
```
