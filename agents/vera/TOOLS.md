# TOOLS.md — Vera
**sim_id:** VRA-CFO

## Tool Usage Conventions

### Token Ledger (via VRA-TKL-01)
- All `token_ledger` reads and writes go through VRA-TKL-01 — never query Postgres directly
- Daily reset runs at 00:00 UTC — confirm `BUDGET_RESET` event after each reset
- On VRA-TKL-01 unavailable: block all new clearances, alert Roxy, await restoration

### Model Tier Assignment (via VRA-MDL-01)
- Every clearance request must include a model tier in the response
- VRA-MDL-01 handles routing logic using `profit_equilibrium_formula.md` rates
- On VRA-MDL-01 unavailable: default all assignments to ECONOMY, note in clearance record

### ROI Scoring (via VRA-ROI-01)
- Required for all STRATEGY domain tasks and any task involving capital deployment
- Returns: `roi_score`, `break_even_months`, `capital_risk`
- On VRA-ROI-01 unavailable: flag clearance as `PENDING_ROI_SCORE`, hold until restored

### Clearance Webhook
- Clearance requests arrive at `/vera-clearance-request`
- Respond with clearance record JSON — include `clearance_id` for Brom's `vera_clearance_ref`
- Always respond within 5 minutes — stalled clearances trigger Roxy notification

### Ledger Writes
- `HEGEMON_AUDIT_WEBHOOK` for all clearance and budget events
- `HEGEMON_TOKEN_WEBHOOK` for token usage reporting (Workflow 10)
- Both webhooks must be confirmed reachable at session start

### Budget Alert Routing
- YELLOW/RED alerts → `HEGEMON_TO_TELEGRAM` via Workflow 02
- EXCEEDED blocks → Workflow 10 handles automatically; Vera logs `RED_FLAG_TRIGGERED`
