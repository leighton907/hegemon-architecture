# TOOLS.md — Roxy
**sim_id:** RXY-CEO

## Tool Usage Conventions

### Webhook Calls (n8n)
- Always include `task_id` and `origin` in every POST payload
- Always include `X-Hegemon-Token` header
- Log `ROUTING_COMPLETE` to ledger after every successful dispatch

### Ledger Writes
- Use Workflow 05 endpoint (`HEGEMON_AUDIT_WEBHOOK`) — never write directly to Postgres
- Every ledger call must include `event_id`, `actor: RXY-CEO`, `action`, `outcome`, `timestamp`

### Telegram (outbound)
- Route through Workflow 02 (`HEGEMON_TO_TELEGRAM`) — never call Telegram API directly
- Keep alerts under 200 characters where possible
- Format: `[STATUS] AGENT — description — Task: {task_id}`

### File Access
- Corpus files: read-only
- No writes to any file outside session state
- Config lookups: `agent_schema.yaml` and `doctrine_tree.yaml` are primary references

### Tool Authorization
- Check `tool_policy.py` via `engine.check_tool()` before any non-standard tool use
- If authorization returns `DENIED_NEEDS_VOTE` → initiate Council vote before proceeding
