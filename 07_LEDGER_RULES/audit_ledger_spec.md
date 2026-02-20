# Audit Ledger Specification
**Document ID:** LDG-002
**Version:** 1.0
**Status:** Active
**Authority:** Architect Command Manifest v2.5 — Section 3
**Owned by:** Brom (BRM-CTO) — enforcement
**Consumed by:** All agents, Workflow 05 (Audit Ledger Logger), Workflow 10 (Token Budget Monitor)

---

## Purpose

This document defines the authoritative schema for every record written to the Hegemon audit ledger. All agents, sub-agents, and workers that write to the ledger must conform to this spec. Workflow 05 enforces this schema at the webhook level. No record that deviates from this schema is accepted.

The ledger is the institutional memory of Hegemon. It is append-only, tamper-evident, and permanent. Nothing is deleted from the ledger.

---

## Database: Tables Overview

The Hegemon audit ledger uses Postgres with four tables:

| Table | Purpose | Written By |
|-------|---------|------------|
| `audit_events` | All agent actions, security events, system events | All agents via Workflow 05 |
| `token_ledger` | Per-agent token usage and daily spend | Vera / Workflow 10 |
| `decision_trails` | Council vote records and proposal outcomes | Roxy and Brom |
| `economic_metrics` | Venture revenue, budget limits, cost tracking | Vera |

---

## Table 1: audit_events

The primary ledger table. Every significant action in Hegemon produces an entry here.

### Schema

```sql
CREATE TABLE IF NOT EXISTS audit_events (
  id               SERIAL PRIMARY KEY,
  event_id         VARCHAR(255) UNIQUE NOT NULL,
  actor            VARCHAR(50)  NOT NULL,
  action           TEXT         NOT NULL,
  outcome          VARCHAR(20)  NOT NULL,
  details          JSONB,
  task_id          VARCHAR(255),
  timestamp        TIMESTAMP    NOT NULL,
  integrity_hash   VARCHAR(64)  NOT NULL,
  created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actor     ON audit_events(actor);
CREATE INDEX idx_outcome   ON audit_events(outcome);
CREATE INDEX idx_timestamp ON audit_events(timestamp);
CREATE INDEX idx_task_id   ON audit_events(task_id);
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | VARCHAR(255) | **Required** | Unique identifier. Format: `{PREFIX}-{actor}-{timestamp_ms}`. Examples: `SEC-RXY-CEO-1708451234567`, `EXEC-BRM-CTO-1708451234568` |
| `actor` | VARCHAR(50) | **Required** | The sim_id of the agent that produced this event. Must match a registered agent in `agent_schema.yaml`. Examples: `RXY-CEO`, `SRN-MRS-01`, `WRK-006`, `N8N_SANITIZER`, `ARCHITECT` |
| `action` | TEXT | **Required** | SCREAMING_SNAKE_CASE description of what happened. See Action Registry below. |
| `outcome` | VARCHAR(20) | **Required** | One of: `SUCCESS`, `FAILURE`, `BLOCKED`, `PENDING`, `WARNING`, `APPROVED`, `REJECTED`, `PARTIAL` |
| `details` | JSONB | Optional | Structured metadata about the event. Schema varies by action type — see Details Schema section. |
| `task_id` | VARCHAR(255) | Optional | The originating task ID if this event traces to a task. Links events to their source task. |
| `timestamp` | TIMESTAMP | **Required** | UTC timestamp of when the event occurred (not when it was written). ISO8601 format in API calls. |
| `integrity_hash` | VARCHAR(64) | **Required** | SHA256 hash of `event_id + actor + action + outcome + timestamp` concatenated. Computed by WRK-008 or Workflow 05. |

### Event ID Format

```
{PREFIX}-{ACTOR_SIM_ID}-{UNIX_TIMESTAMP_MS}

Prefixes by event type:
  EXEC   — execution events (Brom)
  VOTE   — Council vote events (Roxy)
  PROP   — proposal events (Sorin)
  CLR    — economic clearance events (Vera)
  SEC    — security events (any agent)
  TOOL   — tool authorization events
  SYS    — system events (n8n, watchdog)
  ROUTE  — routing events (Workflow 06)
  CORP   — corpus events (Astra)
  N8N    — n8n workflow events
  ERR    — error events
```

### Action Registry

All valid action values. Agents must use these exact strings.

**Roxy (RXY-CEO):**
| Action | Outcome Values | Description |
|--------|----------------|-------------|
| `TASK_RECEIVED` | SUCCESS, FAILURE | Task received from intake |
| `SUBTASK_DISPATCHED` | SUCCESS | Sub-task sent to agent |
| `COUNCIL_CONVENED` | SUCCESS | Council vote initiated |
| `VOTE_RECORDED` | APPROVED, REJECTED | Vote outcome logged |
| `HITL_ISSUED` | BLOCKED | Human-in-the-loop pause triggered |
| `ROUTING_COMPLETE` | SUCCESS, FAILURE | Task routed to destination agent |
| `DECOMPOSITION_COMPLETE` | SUCCESS | Compound task decomposed into sub-tasks |

**Sorin (SRN-CIO):**
| Action | Outcome Values | Description |
|--------|----------------|-------------|
| `ANALYSIS_STARTED` | SUCCESS | Research/analysis task begun |
| `PROPOSAL_SUBMITTED` | SUCCESS | Proposal package sent to Roxy |
| `VOTE_CAST` | APPROVED, REJECTED, ABSTAIN | Sorin's Council vote |
| `SUBTASK_DISPATCHED` | SUCCESS | Sub-agent dispatched |
| `RESEARCH_COMPLETE` | SUCCESS, FAILURE | Research phase finished |
| `CONFIDENCE_FLAGGED` | WARNING | Confidence rating is LOW — flagged |

**Brom (BRM-CTO):**
| Action | Outcome Values | Description |
|--------|----------------|-------------|
| `EXECUTION_STARTED` | SUCCESS | Approved task execution begun |
| `EXECUTION_COMPLETED` | SUCCESS, FAILURE, PARTIAL | Task execution finished |
| `SUBTASK_DISPATCHED` | SUCCESS | Sub-agent dispatched |
| `WORKFLOW_TRIGGERED` | SUCCESS, FAILURE | n8n workflow triggered |
| `AGENT_VALIDATED` | APPROVED, REJECTED | Agent definition validated against schema |
| `LEDGER_WRITTEN` | SUCCESS, FAILURE | Ledger entry confirmed |
| `VOTE_CAST` | APPROVED, REJECTED, ABSTAIN | Brom's Council vote |
| `INFRA_CHANGE` | SUCCESS, FAILURE, ROLLBACK | Infrastructure modified |

**Vera (VRA-CFO):**
| Action | Outcome Values | Description |
|--------|----------------|-------------|
| `CLEARANCE_ISSUED` | APPROVED, BLOCKED | Economic clearance decision |
| `BUDGET_UPDATED` | SUCCESS | Token ledger updated |
| `RED_FLAG_TRIGGERED` | BLOCKED | Financial red-flag fired |
| `ROI_SCORED` | SUCCESS | Venture ROI calculated |
| `MODEL_TIER_ASSIGNED` | SUCCESS | Model tier routing decision |
| `BUDGET_REPORT_SENT` | SUCCESS | Hourly/weekly report sent |
| `VOTE_CAST` | APPROVED, REJECTED, ABSTAIN | Vera's Council vote |
| `BUDGET_RESET` | SUCCESS | Daily budget reset at 00:00 UTC |

**Astra (AST-GOV):**
| Action | Outcome Values | Description |
|--------|----------------|-------------|
| `CORPUS_AUDIT` | SUCCESS, FAILURE | Corpus consistency scan |
| `VIOLATION_FLAGGED` | BLOCKED | Governance violation detected |
| `CP_SUBMITTED` | PENDING | Change proposal submitted to Architect |
| `DOC_VALIDATED` | APPROVED, REJECTED | Document validated against doctrine |
| `HANDOFF_PRODUCED` | SUCCESS | Dev-to-production handoff document created |

**Security events (any agent):**
| Action | Outcome Values | Description |
|--------|----------------|-------------|
| `INJECTION_SCAN` | SUCCESS, WARNING, BLOCKED | injection_guard.py inspection result |
| `INJECTION_BLOCKED_AT_INTAKE` | BLOCKED | n8n sanitization node blocked input |
| `TOOL_REQUEST_{TOOL_NAME}` | AUTHORIZED, DENIED, DENIED_NEEDS_VOTE, DENIED_NEEDS_ARCHITECT | tool_policy.py authorization result |

**System/n8n events:**
| Action | Outcome Values | Description |
|--------|----------------|-------------|
| `TASK_INTAKE` | SUCCESS, FAILURE | Workflow 01 received a task |
| `TASK_DISPATCHED` | SUCCESS, FAILURE | Workflow 06 routed a task |
| `AUTO_APPROVED` | APPROVED | Low-priority task bypassed Council vote |
| `SECRET_ROTATED` | SUCCESS | API key or credential rotated |
| `CONTEXT_COMPRESSED` | SUCCESS | Agent context compressed to save tokens |

### Details Schema by Action Type

The `details` JSONB field has these standard structures:

**For INJECTION_SCAN:**
```json
{
  "severity": "CRITICAL|HIGH|MEDIUM|LOW|CLEAN",
  "matched_patterns": ["CRITICAL", "HIGH"],
  "input_source": "telegram",
  "input_length": 142,
  "blocked": true,
  "sanitized": false
}
```

**For TOOL_REQUEST_*:**
```json
{
  "tool_name": "n8n_trigger",
  "agent_tier": "TIER_1_COUNCIL",
  "council_vote_ref": "VOTE-RXY-CEO-...",
  "architect_approval_ref": null
}
```

**For CLEARANCE_ISSUED:**
```json
{
  "model_tier_assigned": "STANDARD",
  "estimated_token_cost": 0.045,
  "current_daily_spend": 1.23,
  "budget_status": "GREEN",
  "roi_score": "HIGH",
  "clearance_decision": "APPROVED",
  "block_reason": null
}
```

**For EXECUTION_COMPLETED:**
```json
{
  "proposal_id": "SRN-TEL-...-...",
  "council_vote_ref": "VOTE-RXY-CEO-...",
  "steps_completed": 4,
  "steps_total": 4,
  "n8n_workflows_triggered": ["HEGEMON-09", "HEGEMON-05"],
  "error": null
}
```

**For VOTE_RECORDED:**
```json
{
  "proposal_id": "SRN-TEL-...-...",
  "votes": {
    "RXY-CEO": "APPROVED",
    "SRN-CIO": "APPROVED",
    "BRM-CTO": "APPROVED",
    "VRA-CFO": "APPROVED"
  },
  "result": "APPROVED",
  "threshold_required": 2,
  "threshold_met": true
}
```

---

## Table 2: token_ledger

Tracks per-agent daily token usage for Vera's budget enforcement.

### Schema

```sql
CREATE TABLE IF NOT EXISTS token_ledger (
  agent_name          VARCHAR(50)    NOT NULL,
  date                DATE           NOT NULL,
  total_tokens_input  INTEGER        DEFAULT 0,
  total_tokens_output INTEGER        DEFAULT 0,
  total_cost          DECIMAL(10,4)  DEFAULT 0,
  last_updated        TIMESTAMP,
  budget_status       VARCHAR(20),
  PRIMARY KEY (agent_name, date)
);
```

### Field Definitions

| Field | Description |
|-------|-------------|
| `agent_name` | The sim_id of the agent (e.g. `RXY-CEO`) |
| `date` | UTC date (resets daily at 00:00 UTC) |
| `total_tokens_input` | Cumulative input tokens consumed today |
| `total_tokens_output` | Cumulative output tokens produced today |
| `total_cost` | Cumulative USD cost today |
| `last_updated` | Timestamp of most recent update |
| `budget_status` | Current status: GREEN / YELLOW / RED / EXCEEDED |

Written by Vera (VRA-TKL-01 sub-agent) after every model call via Workflow 10.

---

## Table 3: decision_trails

Records every Council vote and its outcome. The institutional record of governance decisions.

### Schema

```sql
CREATE TABLE IF NOT EXISTS decision_trails (
  id            SERIAL PRIMARY KEY,
  trail_id      VARCHAR(255) UNIQUE NOT NULL,
  council_vote  JSONB        NOT NULL,
  proposal      JSONB        NOT NULL,
  outcome       VARCHAR(20)  NOT NULL,
  ledger_ref    VARCHAR(255),
  created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
```

### Field Definitions

| Field | Description |
|-------|-------------|
| `trail_id` | Unique ID: `TRAIL-{proposal_id}-{timestamp_ms}` |
| `council_vote` | JSON of all votes cast: `{"RXY-CEO": "APPROVED", "SRN-CIO": "APPROVED", ...}` |
| `proposal` | JSON summary of the proposal: `{proposal_id, task_id, description, sorin_confidence, vera_clearance}` |
| `outcome` | `APPROVED`, `REJECTED`, `TIMEOUT`, `VETOED` |
| `ledger_ref` | Reference to the corresponding audit_events row (event_id of VOTE_RECORDED) |

Written by Roxy (RXY-CEO) after every Council vote via Workflow 07.

---

## Table 4: economic_metrics

Stores venture revenue, dynamic budget limits, and system-level financial metrics.

### Schema

```sql
CREATE TABLE IF NOT EXISTS economic_metrics (
  id            SERIAL PRIMARY KEY,
  metric_key    TEXT        NOT NULL,
  metric_value  DECIMAL(12,4) NOT NULL,
  period        VARCHAR(20),
  set_by        VARCHAR(50),
  created_at    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metric_key ON economic_metrics(metric_key);
```

### Standard Metric Keys

| metric_key format | Example | Description |
|-------------------|---------|-------------|
| `daily_limit_{agent_sim_id}` | `daily_limit_RXY-CEO` | Agent daily budget limit in USD |
| `venture_revenue_{name}_{YYYY-MM}` | `venture_revenue_affiliate_funnel_2026-02` | Monthly venture revenue |
| `operating_cost_{YYYY-MM}` | `operating_cost_2026-02` | Total monthly operating cost |
| `token_rate_{model_tier}_{direction}` | `token_rate_STANDARD_input` | Model pricing rate per 1K tokens |
| `venture_capital_{name}` | `venture_capital_affiliate_funnel` | Total capital deployed to venture |

---

## Integrity Hash Computation

Every `audit_events` record requires an integrity hash. Computed as:

```python
import hashlib

def compute_integrity_hash(event_id, actor, action, outcome, timestamp):
    payload = f"{event_id}{actor}{action}{outcome}{timestamp}"
    return hashlib.sha256(payload.encode()).hexdigest()
```

This is performed by:
- `injection_guard.py` for security events
- `tool_policy.py` for tool authorization events
- `engine.py` for model call events
- WRK-008 (SHA Hash Worker) for all other events
- Workflow 05 as a fallback for any event missing a hash

**Verification:** Astra's Corpus Audit Sub-Agent (AST-AUD-01) may verify ledger integrity by recomputing hashes for any time range and comparing against stored values.

---

## Writing to the Ledger: Agent Protocol

All agents must use one of these methods to write to the ledger:

**Method 1 (preferred): Via Workflow 05 webhook**
POST to `HEGEMON_AUDIT_WEBHOOK` with the full audit event payload.
Workflow 05 handles hash validation and database insertion.

**Method 2: Via WRK-006 (Ledger Entry Worker)**
Spawn WRK-006 with the audit event payload.
WRK-006 POSTs to Workflow 05 and returns the confirmed `event_id` and `integrity_hash`.

**Never:** Write directly to Postgres without going through Workflow 05. Direct DB writes bypass hash generation and integrity checking.

---

## Retention Policy

| Table | Retention |
|-------|-----------|
| `audit_events` | Permanent — never deleted |
| `token_ledger` | 90 days of daily records |
| `decision_trails` | Permanent — never deleted |
| `economic_metrics` | 365 days of metric records |

Archived records older than retention period are exported to cold storage before deletion from the active database. Deletion of `audit_events` or `decision_trails` records is forbidden without explicit Architect authorization via a Ledger entry.

---

## Amendment Process

Schema changes to this spec require a CP-XXXX Change Proposal from Astra and Architect approval. Database migrations must be documented and tested before applying to production. All schema changes are logged as `SCHEMA_MIGRATION` audit events.
