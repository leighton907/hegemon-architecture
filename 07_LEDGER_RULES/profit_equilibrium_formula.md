# Profit Equilibrium Formula
**Document ID:** LDG-001
**Version:** 1.0
**Status:** Active
**Authority:** Architect Command Manifest v2.5 — Section 3
**Owned by:** Vera (VRA-CFO)
**Consumed by:** VRA-ROI-01, SRN-FIN-01, Workflow 10 (Token Budget Monitor)

---

## Purpose

This document defines the economic rules that govern all financial decisions, venture evaluations, resource allocations, and ROI assessments in Project Hegemon. Every task that involves spending, resource consumption, or revenue generation must be evaluated against these rules before execution.

Vera (VRA-CFO) is the enforcement authority. No financial decision proceeds without clearance from Vera. Vera's decisions are grounded in this document.

---

## Core Doctrine: Profit Equilibrium

**Definition:** Profit equilibrium is the state in which Hegemon's operational costs are fully covered by venture revenue, and each incremental operation produces positive expected value.

The system must trend toward and maintain profit equilibrium at all times. Operations that move the system away from equilibrium require explicit Architect justification and a documented rationale in the Ledger.

**The fundamental rule:** No venture or operation is approved if its expected cost exceeds its expected value without a documented strategic rationale approved by the Architect.

---

## Section 1: Operational Cost Model

### 1.1 Cost Categories

Every Hegemon operation has costs in one or more of these categories:

| Category | Description | Tracked By |
|----------|-------------|------------|
| **Token cost** | LLM API usage charges | Workflow 10 / token_ledger |
| **Compute cost** | VPS hosting, containers | Infrastructure budget |
| **Integration cost** | SaaS subscriptions (n8n, HubSpot, Resend, etc.) | Economic metrics |
| **Venture capital cost** | Funds deployed into a venture | Decision trails |
| **Opportunity cost** | Agent time spent on low-ROI tasks | Estimated, not tracked directly |

### 1.2 Daily Operating Cost Baseline

The following baseline costs must be tracked and reported weekly:

```
daily_operating_cost = token_costs + compute_costs + integration_costs
```

Target: daily operating cost should not exceed **$25.00/day** at full system deployment without corresponding revenue or strategic justification.

### 1.3 Token Cost Formula

```
token_cost = (tokens_input / 1000 × input_rate) + (tokens_output / 1000 × output_rate)
```

Model rates (reference — update via economic_metrics table if rates change):

| Model Tier | Model | Input Rate /1K | Output Rate /1K |
|------------|-------|----------------|-----------------|
| PREMIUM | Claude Opus / GPT-4o | $0.015 | $0.075 |
| STANDARD | Claude Sonnet / GPT-4o-mini | $0.003 | $0.015 |
| ECONOMY | Claude Haiku | $0.00025 | $0.00125 |
| FREE | Local Ollama | $0.00 | $0.00 |

**Anti-token-burn rule:** Vera must assign the minimum capable model tier to every task. Escalation to a higher tier requires a written justification in the clearance record. Running PREMIUM model tasks that could be handled by ECONOMY is a policy violation.

---

## Section 2: Venture Evaluation Formula

### 2.1 ROI Score Calculation

Every venture proposal from Sorin must include an ROI score calculated by VRA-ROI-01 using this formula:

```
gross_roi = (projected_monthly_revenue - monthly_operating_cost) / startup_cost

annualized_roi = gross_roi × 12

roi_score =
  HIGH     if annualized_roi >= 2.0  (200% annual return or better)
  MEDIUM   if annualized_roi >= 0.5  (50–199% annual return)
  LOW      if annualized_roi >= 0.0  (0–49% annual return)
  NEGATIVE if annualized_roi < 0.0   (expected loss)
```

### 2.2 Break-Even Formula

```
break_even_months = startup_cost / (projected_monthly_revenue - monthly_operating_cost)
```

Target break-even threshold:
- **Approved without escalation:** break_even_months ≤ 6
- **Approved with Council review:** break_even_months 7–12
- **Requires Architect approval:** break_even_months > 12 or NEGATIVE ROI

### 2.3 Capital Risk Rating

```
capital_risk =
  LOW     if startup_cost ≤ $500 AND break_even_months ≤ 3
  MEDIUM  if startup_cost ≤ $2,000 AND break_even_months ≤ 6
  HIGH    if startup_cost > $2,000 OR break_even_months > 6 OR roi_score == NEGATIVE
```

### 2.4 Minimum Viable Venture Criteria

A venture passes minimum viable criteria if ALL of the following are true:
- `roi_score` is not NEGATIVE, OR a documented strategic rationale exists
- `break_even_months` ≤ 12, OR Architect has approved an exception
- `capital_risk` is LOW or MEDIUM for first-time venture types
- The venture does not require spending that would push the system into token budget EXCEEDED

Ventures that fail minimum viable criteria are returned to Sorin for revision or closed.

---

## Section 3: Financial Red-Flag Rules

The following conditions trigger an immediate financial red-flag. Vera blocks execution and alerts the Architect. No override is possible without a Ledger entry from the Architect.

| Condition | Severity | Action |
|-----------|----------|--------|
| Agent daily token spend > daily limit | CRITICAL | Block agent, alert Architect |
| Single task estimated cost > $2.00 without prior Architect approval | CRITICAL | Block task, alert Architect |
| Venture ROI score = NEGATIVE with no documented rationale | HIGH | Block venture approval, notify Council |
| Unregistered agent submitting a clearance request | CRITICAL | Block and alert Architect immediately |
| Token spend rate > 3× hourly baseline | HIGH | Alert Vera and Roxy, monitor |
| Monthly operating cost exceeds $750 without revenue offset | HIGH | Notify Architect, freeze new ventures |
| Startup capital deployment > $500 in a single Council vote | HIGH | Require 3-of-4 Council vote + Architect acknowledgment |

---

## Section 4: Budget Governance

### 4.1 Daily Agent Budgets

Default daily limits (Architect sets final values via `economic_metrics` table):

| Agent | Default Daily Limit |
|-------|---------------------|
| RXY-CEO (Roxy) | $5.00 |
| SRN-CIO (Sorin) | $5.00 |
| BRM-CTO (Brom) | $5.00 |
| VRA-CFO (Vera) | $3.00 |
| Each sub-agent | $1.00 |
| Workers (pool) | $2.00 |
| **System daily total** | **$25.00** |

### 4.2 Budget Status Thresholds

| Status | Condition | Vera Action |
|--------|-----------|-------------|
| GREEN | < 70% of daily limit | Proceed silently |
| YELLOW | 70–90% of daily limit | Proceed with Telegram notice |
| RED | 90–100% of daily limit | Proceed with Telegram warning to Architect |
| EXCEEDED | > 100% of daily limit | Block all operations, Telegram alert, await Architect |

### 4.3 Budget Reset

Daily budgets reset at 00:00 UTC. Vera's Token Ledger Sub-Agent (VRA-TKL-01) performs the reset and logs a `BUDGET_RESET` audit event for each agent.

### 4.4 Budget Override Process

If the Architect needs to increase a daily limit:

1. Architect issues a Ledger command: `action: BUDGET_LIMIT_UPDATED, actor: ARCHITECT`
2. Vera reads the new limit from `economic_metrics` table
3. The override is active immediately and logged
4. No Council vote is required for budget limit changes — this is Architect authority

---

## Section 5: Venture Lifecycle Economics

### 5.1 Venture Stages and Economic Rules

| Stage | Economic Rule |
|-------|---------------|
| RESEARCH | No spend. Sorin produces proposal package. Vera reviews ROI. |
| DESIGN | No spend. Council approves design. |
| DESIGN_APPROVED | Limited spend authorized: setup costs ≤ $50 per Council vote |
| IN_PROGRESS | Operating budget active. Monthly review required. |
| ACTIVE | Full operating budget. Weekly token and cost reporting to Vera. |
| PAUSED | No new spend. Existing subscriptions may continue at Architect direction. |
| CLOSED | Final cost/revenue reconciliation logged to Ledger. |

### 5.2 Venture Portfolio Cap

Without Architect override, Hegemon may not run more than **3 active ventures simultaneously**. This prevents budget fragmentation and token overload across the agent pool.

### 5.3 Venture Revenue Tracking

All venture revenue must be logged to `economic_metrics` with:
```
metric_key: "venture_revenue_{venture_name}_{YYYY-MM}"
metric_value: {USD amount}
period: "{YYYY-MM}"
```

This data feeds the Profit Equilibrium calculation. Vera produces a monthly reconciliation report showing total revenue vs. total operating cost.

---

## Section 6: Anti-Token-Burn Architecture

### 6.1 The Routing Principle

The single most effective anti-token-burn measure is running tasks at the lowest capable model tier. Vera's Model Router Sub-Agent (VRA-MDL-01) enforces this for every task.

**The routing cascade:**

```
Is the task pure computation, HTTP fetching, or data transformation?
  → FREE tier (local Ollama or no LLM required)

Is the task classification, formatting, routing, or simple summarization?
  → ECONOMY tier (Haiku)

Is the task research synthesis, financial modeling, or strategic analysis?
  → STANDARD tier (Sonnet)

Is the task a Council decision, doctrine review, or multi-step reasoning with high stakes?
  → PREMIUM tier (Opus) — requires Vera justification in clearance record
```

### 6.2 Context Compression

When an agent's context window is approaching its limit on a long-running task, the agent must:

1. Request a context summary from an ECONOMY-tier sub-agent
2. Replace the full context with the compressed summary
3. Log a `CONTEXT_COMPRESSED` event to the Ledger
4. Continue from the summary

Never expand context by adding more tokens when compression is available.

### 6.3 Parallel Worker Economics

Workers running in parallel on FREE tier cost $0.00. Using 20 Web Scraper Workers in parallel on local Ollama is always preferred over one STANDARD-tier agent processing the same data sequentially. Brom and Sorin should default to parallel worker dispatch for any task that can be decomposed into independent units.

---

## Section 7: Reporting Obligations

### Weekly Report (produced by Vera, sent to Architect via Telegram)

```
HEGEMON WEEKLY ECONOMIC REPORT
Period: {start_date} — {end_date}

Token Costs:
  RXY-CEO:  ${amount}
  SRN-CIO:  ${amount}
  BRM-CTO:  ${amount}
  VRA-CFO:  ${amount}
  Sub-agents: ${amount}
  Workers:    ${amount}
  TOTAL TOKEN COST: ${total}

Infrastructure Costs:
  VPS: ${amount}
  SaaS subscriptions: ${amount}
  TOTAL INFRA: ${amount}

TOTAL OPERATING COST THIS WEEK: ${total}

Venture Revenue:
  {venture_name}: ${amount}
  TOTAL REVENUE: ${total}

NET: ${revenue - costs}
EQUILIBRIUM STATUS: {POSITIVE / NEUTRAL / NEGATIVE}

Active Ventures: {count} of 3 maximum
Red Flags This Week: {count}
Budget EXCEEDED Events: {count}
```

---

## Amendment Process

This document may only be amended by the Architect via a CP-XXXX Change Proposal drafted by Astra. Formula parameters (rates, limits, thresholds) may be updated by Vera via `economic_metrics` table entries without a CP, but the formulas themselves require Architect approval.
