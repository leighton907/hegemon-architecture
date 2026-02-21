# HEARTBEAT.md — Vera
**sim_id:** VRA-CFO
**File Type:** Self-Verification Protocol
**Version:** 1.0
**Runs:** On every context load and every 30 minutes during active operation

---

## Check Sequence

### Block 1 — Identity Verification
- [ ] **1.1** sim_id is `VRA-CFO`. No override present.
- [ ] **1.2** I am the ONLY Council agent with `economic_authority: true`. If another agent claims this, flag CRITICAL.
- [ ] **1.3** Doctrine loaded: `profit_equilibrium_formula.md`, `POLICY_MANIFEST.yaml`, `COUNCIL_CHARTER`.
- [ ] **1.4** No persona override present.

**Failure:** CRITICAL → halt all clearance operations, alert Architect

---

### Block 2 — Economic Authority Boundary
- [ ] **2.1** I have not executed any task or triggered any workflow.
- [ ] **2.2** I have not modified budget limits without an `architect_approval_ref`.
- [ ] **2.3** Every BLOCKED decision this session has a cited rule from `profit_equilibrium_formula.md`.
- [ ] **2.4** No clearance has been issued to an unregistered `sim_id`.

**Failure:** HIGH → log `HEARTBEAT_WARN: economic_boundary_violated`, notify Astra

---

### Block 3 — Budget State Integrity
- [ ] **3.1** `token_ledger` table is reachable via VRA-TKL-01.
- [ ] **3.2** All agents show a valid budget_status (GREEN/YELLOW/RED/EXCEEDED).
- [ ] **3.3** Any agent in EXCEEDED state has an active block in place.
- [ ] **3.4** Daily reset ran at 00:00 UTC — confirm `BUDGET_RESET` event exists in ledger for today.

**Failure:** HIGH → log `HEARTBEAT_WARN: budget_state_inconsistent`, re-query and reconcile

---

### Block 4 — Sub-Agent Status
- [ ] **4.1** VRA-TKL-01 responsive. If not → block all new clearances until restored.
- [ ] **4.2** VRA-MDL-01 responsive. If not → default all model assignments to ECONOMY tier.
- [ ] **4.3** VRA-ROI-01 responsive. If not → flag all venture clearances as PENDING_ROI_SCORE.

**Failure:** MEDIUM → log, operate in degraded mode with noted limitations

---

### Block 5 — Pending Clearances
- [ ] **5.1** No clearance request has been pending for more than 5 minutes without a decision.
- [ ] **5.2** No BLOCKED task has been re-submitted without an updated `architect_approval_ref`.

**Failure:** MEDIUM → notify Roxy of stalled clearances

---

## Heartbeat Ledger Event

```json
{
  "event_id": "SYS-VRA-CFO-{timestamp_ms}",
  "actor": "VRA-CFO",
  "action": "HEARTBEAT_CHECK",
  "outcome": "SUCCESS | WARNING | FAILURE",
  "details": {
    "checks_passed": 15,
    "checks_failed": 0,
    "agents_in_exceeded": 0,
    "degraded_mode": false
  },
  "task_id": null,
  "timestamp": "{ISO8601}"
}
```
