# TOOLS.md — Astra
**sim_id:** AST-GOV

## Tool Usage Conventions

### Corpus Reads
- All files in the repo are readable — use exact paths from `grounding_sources_index` in `doctrine_tree.yaml`
- Read frequently: COUNCIL_CHARTER, COUNCIL_PROTOCOLS, agent_schema, doctrine_tree, POLICY_MANIFEST
- Never modify corpus files directly — draft CP-XXXX and await Architect approval

### Corpus Audit (via AST-AUD-01)
- Scheduled: run monthly automatically
- On-demand: trigger when a new file is added or a governance concern arises
- Returns: gap inventory with severity ratings
- All findings logged as `CORPUS_AUDIT` events with `details.gaps` array

### Change Proposal Drafting (via AST-CPD-01)
- Trigger for every gap rated HIGH or CRITICAL
- Output goes to `/astra-governance-request` for Architect review
- Never self-approve — every CP stays `PENDING_ARCHITECT_REVIEW` until Architect ledger entry

### Doctrine Compliance (via AST-DCL-01)
- Called by Roxy before every Council vote on BUILD or GOVERNANCE tasks
- Returns: APPROVED or REJECTED with specific violations listed
- Turnaround: < 5 minutes per validation

### Vote Suspension
- Mechanism: POST to Roxy at `/roxy-task-receive` with `action: SUSPEND_VOTE`, `proposal_id`, `violation_reason`
- Only Architect can lift a suspended vote — Astra cannot lift her own suspensions

### Ledger Writes
- `HEGEMON_AUDIT_WEBHOOK` for all governance events
- Include `violation_ref` in details for any flagged event

### Handoff Package
- Maintained as a living document in session state
- Updated every session — commit to corpus as `docs/PRODUCTION_ASTRA_HANDOFF.md` before dev retirement
