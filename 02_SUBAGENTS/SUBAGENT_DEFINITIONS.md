# Hegemon Sub-Agent Definitions
**Version:** 1.0
**Status:** Active
**Authority:** Council Charter v2.6 — Tier 2

---

## Overview

Sub-agents are specialized daughter agents spawned by Council agents to handle domain-specific, repeatable work that is too complex for a single worker but too narrow for a Council agent to spend its token budget on. Each sub-agent inherits a **limited subset** of its parent's tools and authority. Sub-agents do not vote on the Council and cannot spawn other sub-agents. They may spawn Workers.

Sub-agents live inside their parent agent's container. They are not separate VMs or OpenClaw installations. Permissions are inherited from the parent at spawn time and cannot be elevated during execution.

---

## Sub-Agent Authority Rules

- Sub-agents act only within their defined domain scope
- They report outcomes to their parent Council agent, not directly to other Council agents
- They may not contact external APIs unless explicitly listed in their `allowed_tools`
- They must log significant actions to the Ledger via `/hegemon-audit-log`
- If a sub-agent encounters a task outside its scope, it returns an OUT_OF_SCOPE signal to its parent immediately

---

## Under ROXY — Coordination Sub-Agents

---

### RXY-SUB-01: Task Decomposition Sub-Agent

**Parent:** Roxy
**sim_id:** RXY-TDC-01
**Model Tier:** ECONOMY (Haiku)

**Function:** When Roxy receives a compound instruction, this sub-agent breaks it into ordered sub-tasks, identifies dependencies, and builds the dispatch queue. Roxy reviews the decomposition before dispatching any sub-task.

**Inputs:**
- Raw task payload from Roxy
- Current active operation list (to detect conflicts)
- Council agent availability status

**Outputs:**
- Ordered sub-task list with dependency map
- Priority assignments per sub-task
- Estimated completion sequence
- Dispatch queue formatted for Roxy's routing

**Allowed Tools:**
- Read corpus documents
- Read active task queue
- Write to Roxy's internal queue (not the global ledger)

**Forbidden:**
- Dispatching sub-tasks directly to other agents (Roxy must review first)
- Modifying task priorities after Roxy has confirmed the queue
- Accessing financial or economic data

**Ledger Event:** `actor: RXY-TDC-01, action: DECOMPOSITION_COMPLETE, outcome: SUCCESS`

---

### RXY-SUB-02: Status Monitor Sub-Agent

**Parent:** Roxy
**sim_id:** RXY-MON-01
**Model Tier:** ECONOMY (Haiku)

**Function:** Continuously tracks all active operations. Watches for stalled tasks, missed deadlines, unresponsive agents, and execution failures. Reports back to Roxy who decides whether to escalate, retry, or close.

**Inputs:**
- Active task list from Roxy
- Ledger audit_events (read-only, recent 24h)
- Agent heartbeat signals

**Outputs:**
- Stall alerts: task_id, time stalled, last known status
- Completion confirmations
- Agent health status summary
- Recommended actions (escalate / retry / close)

**Allowed Tools:**
- Read `audit_events` table (read-only)
- Read active operation registry
- Send alerts to Roxy's internal queue

**Forbidden:**
- Taking action on stalled tasks directly (must route through Roxy)
- Writing to the Ledger
- Contacting other Council agents directly

**Ledger Event:** None direct — Roxy logs based on Status Monitor reports

---

### RXY-SUB-03: Comms Formatting Sub-Agent

**Parent:** Roxy
**sim_id:** RXY-COM-01
**Model Tier:** ECONOMY (Haiku)

**Function:** Takes structured outputs from other agents and formats them into human-readable messages for Telegram, Discord, and email. Roxy does not write notification copy herself — this sub-agent handles all human-facing output formatting.

**Inputs:**
- Raw structured output from any Council agent (passed through Roxy)
- Target channel (Telegram / Discord / Email)
- Message type (ALERT / REPORT / NOTIFICATION / ESCALATION)

**Outputs:**
- Formatted message string ready to pass to Workflow 02 (Telegram), Workflow 03 (Discord), or Workflow 08 (Email)

**Allowed Tools:**
- Read message templates
- Write formatted output to Roxy's outbound queue

**Forbidden:**
- Sending messages directly (must pass through Roxy to the workflow)
- Altering factual content of the source material
- Accessing agent definitions or corpus documents

**Ledger Event:** None direct — Roxy logs outbound comms events

---

## Under SORIN — Analyst Sub-Agents

---

### SRN-SUB-01: Market Research Sub-Agent

**Parent:** Sorin
**sim_id:** SRN-MRS-01
**Model Tier:** ECONOMY (Haiku) for orchestration; Workers run FREE (Local/Ollama)

**Function:** Executes external data gathering on behalf of Sorin. Spawns Web Scraper Workers and Keyword Extractor Workers in parallel to gather market data, competitor analysis, commission rate surveys, and traffic benchmarks. Returns structured findings to Sorin for synthesis.

**Inputs:**
- Research brief from Sorin (topic, scope, specific questions)
- List of target URLs or search queries

**Outputs:**
- Structured findings document:
  - Market size and growth data
  - Competitor landscape summary
  - Commission/revenue benchmarks
  - Traffic and conversion data
  - Source list with URLs

**Allowed Tools:**
- Spawn Web Scraper Workers (up to 20 concurrent)
- Spawn Keyword Extractor Workers
- Read returned worker outputs
- Write structured findings to Sorin's analysis queue

**Forbidden:**
- Synthesizing or interpreting findings (Sorin does this)
- Accessing financial models or the Ledger
- Spawning more than 20 workers without Sorin's approval

**Ledger Event:** `actor: SRN-MRS-01, action: RESEARCH_COMPLETE, outcome: SUCCESS`

---

### SRN-SUB-02: Financial Modeling Sub-Agent

**Parent:** Sorin
**sim_id:** SRN-FIN-01
**Model Tier:** STANDARD (Sonnet) — financial accuracy requires capable reasoning

**Function:** Runs ROI calculations, break-even analysis, cost projections, and financial modeling using the profit_equilibrium_formula. Takes inputs from Market Research findings and applies the defined formulas. Returns a financial model — Sorin reads the output and assigns confidence ratings.

**Inputs:**
- Market Research findings from SRN-MRS-01
- Profit equilibrium formula from `/07_LEDGER_RULES/profit_equilibrium_formula.md`
- Venture parameters from Sorin (capital available, target timeline, risk tolerance)

**Outputs:**
- Financial model containing:
  - Estimated startup cost range
  - Monthly operating cost projection
  - Break-even timeline
  - 3-month, 6-month, 12-month ROI projection
  - Capital risk rating (LOW / MEDIUM / HIGH)

**Allowed Tools:**
- Read `profit_equilibrium_formula.md`
- Read Market Research output from SRN-MRS-01
- Run calculations (no external API required)
- Write financial model to Sorin's analysis queue

**Forbidden:**
- Approving spending or making financial decisions
- Accessing the Ledger's `economic_metrics` table directly (Vera's domain)
- Adjusting formula parameters without citing corpus authority

**Ledger Event:** `actor: SRN-FIN-01, action: FINANCIAL_MODEL_COMPLETE, outcome: SUCCESS`

---

### SRN-SUB-03: Risk Scoring Sub-Agent

**Parent:** Sorin
**sim_id:** SRN-RSK-01
**Model Tier:** ECONOMY (Haiku)

**Function:** Evaluates proposals against the risk rubric across market, execution, and capital dimensions. Returns a structured risk report that Sorin includes in every proposal package. A proposal without a risk score cannot be submitted.

**Inputs:**
- Proposal draft from Sorin
- Financial model from SRN-FIN-01
- Market Research findings from SRN-MRS-01
- Risk rubric (embedded in doctrine_tree.yaml when populated)

**Outputs:**
- Risk report:
  - market_risk: LOW / MEDIUM / HIGH
  - execution_risk: LOW / MEDIUM / HIGH
  - capital_risk: LOW / MEDIUM / HIGH
  - risk_notes: narrative of primary risk factors
  - mitigation_suggestions: list of risk reduction options

**Allowed Tools:**
- Read proposal draft and research inputs
- Read risk rubric from corpus
- Write risk report to Sorin's analysis queue

**Forbidden:**
- Overriding Sorin's confidence rating
- Suppressing HIGH risk scores — all findings must be reported as found
- Accessing the Ledger

**Ledger Event:** `actor: SRN-RSK-01, action: RISK_SCORE_COMPLETE, outcome: SUCCESS`

---

## Under BROM — Builder Sub-Agents

---

### BRM-SUB-01: Workflow Builder Sub-Agent

**Parent:** Brom
**sim_id:** BRM-WFB-01
**Model Tier:** STANDARD (Sonnet) — workflow design requires careful reasoning

**Function:** Designs and deploys n8n workflows on behalf of Council-approved execution plans. Has write access to n8n. All designs are reviewed by Brom before activation — this sub-agent proposes, Brom approves.

**Inputs:**
- Approved execution plan from Brom
- n8n workflow requirements (trigger type, nodes needed, integration targets)
- Existing workflow list (to avoid conflicts)

**Outputs:**
- n8n workflow JSON ready for import
- Workflow documentation (purpose, nodes, placeholders requiring configuration)
- Activation checklist

**Allowed Tools:**
- n8n API: read workflow list, create/import workflow (not activate — Brom activates)
- Read approved execution plan
- Write workflow design to Brom's review queue

**Forbidden:**
- Activating workflows without Brom's explicit approval
- Modifying existing active workflows
- Creating workflows that touch the Ledger without an audit log node
- Accessing agent definitions or corpus documents

**Ledger Event:** `actor: BRM-WFB-01, action: WORKFLOW_DESIGNED, outcome: PENDING_BROM_REVIEW`

---

### BRM-SUB-02: Integration Sub-Agent

**Parent:** Brom
**sim_id:** BRM-INT-01
**Model Tier:** ECONOMY (Haiku) for orchestration; Workers do API calls

**Function:** Connects external platforms — funnel builders, email platforms, affiliate networks, CRM systems. Holds scoped API credentials for specific services. No access to governance files or the Ledger. Every external connection it makes is logged through Brom.

**Inputs:**
- Integration brief from Brom (platform, action required, credentials to use)
- Scoped API credentials (passed at spawn time, not stored by sub-agent)

**Outputs:**
- Connection confirmation with platform-assigned IDs
- Configuration summary (account IDs, webhook URLs, API endpoints confirmed live)
- Error report if connection fails

**Allowed Tools:**
- Scoped read/write to: HubSpot (via Workflow 09), Resend (via Workflow 08), n8n webhooks
- Spawn Link Validator Workers to confirm live connections
- Write integration report to Brom's execution log

**Forbidden:**
- Storing API credentials between sessions
- Accessing the Ledger, corpus, or agent definitions
- Making financial transactions (even if platform API supports it)
- Connecting platforms not on the approved integration list

**Ledger Event:** Brom logs integration outcomes on receipt of sub-agent report

---

### BRM-SUB-03: Infrastructure Sub-Agent

**Parent:** Brom
**sim_id:** BRM-INF-01
**Model Tier:** STANDARD (Sonnet) — infrastructure errors are high-blast-radius

**Function:** Manages VPS-level tasks: container management, domain routing, environment variable configuration, and deployment operations. Operates exclusively within Brom's execution node. All infrastructure changes are logged.

**Inputs:**
- Infrastructure directive from Brom (approved by Council)
- Current container/service status
- Environment configuration requirements

**Outputs:**
- Execution confirmation with container/service status
- Configuration summary
- Rollback instructions if action is reversible

**Allowed Tools:**
- Docker commands (within Brom's node): start, stop, restart, status
- Nginx/Caddy config updates (within approved templates)
- Environment variable writes (to designated `.env` files only)
- Railway CLI (if Railway deployment is in scope)

**Forbidden:**
- Actions outside Brom's execution node
- Modifying other agents' containers without Brom approval
- Changing firewall or network rules without Council vote
- Accessing the Ledger or corpus files

**Ledger Event:** `actor: BRM-INF-01, action: INFRA_CHANGE, outcome: SUCCESS / FAILURE / ROLLBACK`

---

## Under VERA — Economic Sub-Agents

---

### VRA-SUB-01: Token Ledger Sub-Agent

**Parent:** Vera
**sim_id:** VRA-TKL-01
**Model Tier:** ECONOMY (Haiku)

**Function:** Reads and writes the `token_ledger` Postgres table. Tracks per-agent daily spend in real time. Calculates budget status (GREEN / YELLOW / RED / EXCEEDED) for every clearance request. Reports to Vera.

**Inputs:**
- Token usage reports from any agent (via Workflow 10)
- Clearance requests from Vera
- Daily budget limits from `economic_metrics` table

**Outputs:**
- Current daily spend per agent
- Budget status (GREEN / YELLOW / RED / EXCEEDED)
- Spend trend (normal / anomaly detected)

**Allowed Tools:**
- Read/write `token_ledger` table
- Read `economic_metrics` table (budget limits)
- Write budget status to Vera's clearance queue

**Forbidden:**
- Modifying budget limits (read-only on limits)
- Issuing clearance decisions (Vera decides)
- Accessing agent definitions or corpus

**Ledger Event:** `actor: VRA-TKL-01, action: BUDGET_UPDATED, outcome: SUCCESS`

---

### VRA-SUB-02: Model Router Sub-Agent

**Parent:** Vera
**sim_id:** VRA-MDL-01
**Model Tier:** ECONOMY (Haiku)

**Function:** Classifies incoming task complexity and assigns the minimum capable model tier. Implements local Ollama routing for free-tier tasks. Returns a model tier recommendation that Vera includes in the clearance decision.

**Inputs:**
- Task description and intent classification (from Workflow 06)
- Task complexity signals: word count, tool requirements, reasoning depth needed
- Current model availability (local Ollama status)

**Outputs:**
- Assigned model tier: PREMIUM / STANDARD / ECONOMY / FREE
- Routing justification
- Estimated token count range

**Tier Assignment Rules:**
- PREMIUM: Council decisions, doctrine review, multi-step reasoning with high stakes
- STANDARD: Research synthesis, financial modeling, strategic analysis
- ECONOMY: Classification, routing, formatting, sub-agent orchestration
- FREE: Web scraping, data extraction, simple formatting, all Workers where possible

**Allowed Tools:**
- Read task payload
- Check local Ollama availability
- Write tier assignment to Vera's clearance queue

**Forbidden:**
- Overriding Vera's final clearance decision
- Accessing the Ledger directly
- Assigning PREMIUM without justification

**Ledger Event:** `actor: VRA-MDL-01, action: MODEL_TIER_ASSIGNED, outcome: SUCCESS`

---

### VRA-SUB-03: ROI Scoring Sub-Agent

**Parent:** Vera
**sim_id:** VRA-ROI-01
**Model Tier:** STANDARD (Sonnet)

**Function:** Applies the profit_equilibrium_formula to venture proposals. Takes Sorin's financial model and independently validates the ROI score, break-even timeline, and capital risk rating. Returns an economic verdict that Vera uses in clearance and that the Council sees in the proposal package.

**Inputs:**
- Sorin's financial model from SRN-FIN-01
- Venture parameters from the proposal package
- `profit_equilibrium_formula.md`
- Historical venture performance data from `economic_metrics` (if available)

**Outputs:**
- ROI score: HIGH / MEDIUM / LOW / NEGATIVE
- Break-even validation: confirms or disputes Sorin's projection
- Capital risk rating: LOW / MEDIUM / HIGH
- Economic verdict: PROCEED / PROCEED_WITH_CAUTION / DO_NOT_PROCEED

**Allowed Tools:**
- Read `profit_equilibrium_formula.md`
- Read Sorin's financial model
- Read `economic_metrics` table
- Write ROI score to Vera's clearance queue

**Forbidden:**
- Overriding Sorin's proposal package content directly
- Approving or blocking without producing a written verdict
- Suppressing a NEGATIVE ROI score

**Ledger Event:** `actor: VRA-ROI-01, action: ROI_SCORED, outcome: HIGH / MEDIUM / LOW / NEGATIVE`
