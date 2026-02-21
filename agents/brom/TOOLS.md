# TOOLS.md — Brom
**sim_id:** BRM-CTO

## Tool Usage Conventions

### n8n Workflow Triggers
- Always confirm `council_vote_ref` and `vera_clearance_ref` in context before calling
- Include both refs in the POST payload to every workflow trigger
- Log `WORKFLOW_TRIGGERED` to ledger immediately after call, before checking response

### Agent Schema Validation
- Load `04_FRAMEWORK/agent_schema.yaml` before any agent creation or modification
- Run all validation_rules checks — reject on first failure, return specific reason to Roxy
- Never register an agent that fails schema validation

### Docker / Infrastructure (via BRM-INF-01)
- BRM-INF-01 drafts the plan — Brom reviews and authorizes — never direct execution
- Requires RED-zone clearance: 3-of-4 Council vote + Architect ref
- Log `INFRA_CHANGE` with full action details before and after

### External Platform APIs (via BRM-INT-01)
- Credentials come from `.env` only — never hardcoded, never in corpus
- BRM-INT-01 handles the actual API calls — Brom reviews outputs
- Log integration results to ledger with `WORKFLOW_TRIGGERED` event

### Ledger Writes
- Every execution step gets its own ledger entry — not just start and end
- If mid-task failure: write `EXECUTION_COMPLETED outcome=PARTIAL` immediately
- Never batch ledger writes — write each step as it completes

### Rollback Conventions
- Before irreversible actions: document rollback plan in the vote record
- On failure: attempt rollback, log `INFRA_CHANGE outcome=ROLLBACK`
- If rollback fails: halt everything, alert Roxy and Architect
