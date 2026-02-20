# Access Matrix
**Document ID:** SEC-002
**Version:** 1.0
**Status:** Active
**Authority:** Architect Command Manifest v2.5 — Section 3

---

## Overview

This matrix defines what every agent, sub-agent, and worker in Hegemon is permitted to read, write, execute, and modify. It is the authoritative source for permission enforcement. `tool_policy.py` in `openclaw_core/` enforces this matrix at runtime — no agent may use a tool not listed as authorized here.

**Permission keys:**
- ✅ Authorized
- ⚠️ Authorized with conditions (see notes)
- ❌ Denied
- 🔒 Requires Council vote
- 👑 Requires Architect approval

---

## Tier 1 — Council Agents

| Action / Resource | Roxy (RXY-CEO) | Sorin (SRN-CIO) | Brom (BRM-CTO) | Vera (VRA-CFO) |
|---|---|---|---|---|
| **Read corpus / doctrine files** | ✅ | ✅ | ✅ | ✅ |
| **Write corpus / doctrine files** | ❌ | ❌ | ❌ | ❌ |
| **Read ledger (audit_events)** | ✅ | ✅ | ✅ | ✅ |
| **Write ledger (audit_events)** | ✅ | ✅ | ✅ | ✅ |
| **Read token_ledger** | ✅ | ✅ | ✅ | ✅ |
| **Write token_ledger** | ❌ | ❌ | ❌ | ✅ |
| **Issue economic clearance** | ❌ | ❌ | ❌ | ✅ |
| **Modify budget limits** | ❌ | ❌ | ❌ | ⚠️ 👑 |
| **Trigger n8n workflows** | ❌ | ❌ | ✅ 🔒 | ❌ |
| **Create n8n workflows** | ❌ | ❌ | ⚠️ 🔒 (via WFB sub-agent) | ❌ |
| **Send Telegram messages** | ✅ | ❌ | ✅ | ✅ |
| **Send email (Resend)** | ✅ | ❌ | ✅ | ❌ |
| **Send Discord messages** | ✅ | ❌ | ❌ | ❌ |
| **Read HubSpot** | ❌ | ✅ | ✅ | ❌ |
| **Write HubSpot** | ❌ | ❌ | ✅ | ❌ |
| **Web search** | ❌ | ⚠️ (via sub-agent only) | ❌ | ❌ |
| **Web scrape** | ❌ | ⚠️ (via WRK-001 only) | ❌ | ❌ |
| **Create / register agents** | ❌ | ❌ | ✅ 🔒 👑 | ❌ |
| **Retire agents** | ❌ | ❌ | ✅ 🔒 👑 | ❌ |
| **Docker / infrastructure** | ❌ | ❌ | ⚠️ 🔒 (via INF sub-agent) | ❌ |
| **Write .env / secrets** | ❌ | ❌ | ⚠️ 🔒 (via INF sub-agent) | ❌ |
| **Council vote** | ✅ | ✅ | ✅ | ✅ |
| **Initiate HITL pause** | ✅ | ✅ | ✅ | ✅ |
| **Spawn sub-agents** | ✅ (RXY subs only) | ✅ (SRN subs only) | ✅ (BRM subs only) | ✅ (VRA subs only) |
| **Spawn workers** | ✅ | ✅ | ✅ | ✅ |

---

## Tier 1 Adjacent — Governance Observer

| Action / Resource | Astra (AST-GOV) |
|---|---|
| **Read corpus / doctrine files** | ✅ (all files) |
| **Write corpus / doctrine files** | ⚠️ 👑 (Architect approval required for every write) |
| **Read ledger** | ✅ |
| **Write ledger** | ✅ (governance events only) |
| **Flag governance violation (halt Council vote)** | ✅ |
| **Submit Change Proposals (CP-XXXX)** | ✅ |
| **Council vote** | ❌ (observer only) |
| **Trigger n8n workflows** | ❌ |
| **Web search / scrape** | ❌ |
| **Spawn sub-agents** | ✅ (AST subs only) |
| **Spawn workers** | ✅ (corpus and hash workers only) |
| **Create / modify agents** | ❌ (drafts proposals only; Brom + Architect execute) |
| **Initiate HITL pause** | ✅ |

---

## Tier 2 — Sub-Agents

### Under Roxy

| Action / Resource | RXY-TDC-01 (Task Decomp) | RXY-MON-01 (Status Monitor) | RXY-COM-01 (Comms Format) |
|---|---|---|---|
| Read corpus | ✅ | ❌ | ✅ (templates only) |
| Read active task queue | ✅ | ✅ | ❌ |
| Write to Roxy's internal queue | ✅ | ✅ | ✅ |
| Read ledger (recent 24h) | ❌ | ✅ | ❌ |
| Write ledger | ❌ | ❌ | ❌ |
| Send Telegram | ❌ | ❌ | ⚠️ (via Roxy only) |
| Spawn workers | ❌ | ❌ | ❌ |

### Under Sorin

| Action / Resource | SRN-MRS-01 (Market Research) | SRN-FIN-01 (Financial Model) | SRN-RSK-01 (Risk Score) |
|---|---|---|---|
| Read corpus | ✅ | ✅ | ✅ |
| Read profit_equilibrium_formula | ❌ | ✅ | ✅ |
| Web search | ✅ | ❌ | ❌ |
| Spawn WRK-001 (scraper) | ✅ (max 20 concurrent) | ❌ | ❌ |
| Spawn WRK-002 (keyword extractor) | ✅ | ❌ | ❌ |
| Read economic_metrics table | ❌ | ❌ | ❌ |
| Write ledger | ✅ (own events) | ✅ (own events) | ✅ (own events) |
| HubSpot read | ✅ | ❌ | ❌ |

### Under Brom

| Action / Resource | BRM-WFB-01 (Workflow Builder) | BRM-INT-01 (Integration) | BRM-INF-01 (Infrastructure) |
|---|---|---|---|
| n8n read workflow list | ✅ | ❌ | ❌ |
| n8n create workflow | ✅ (propose only — Brom activates) | ❌ | ❌ |
| n8n activate workflow | ❌ | ❌ | ❌ |
| External platform APIs (HubSpot, Resend) | ❌ | ✅ (scoped credentials) | ❌ |
| Docker manage | ❌ | ❌ | ✅ 🔒 |
| Write .env files | ❌ | ❌ | ✅ 🔒 |
| Nginx / Caddy config | ❌ | ❌ | ✅ 🔒 (approved templates only) |
| Spawn WRK-003 (link validator) | ❌ | ✅ | ❌ |
| Spawn WRK-005 (HubSpot updater) | ❌ | ✅ | ❌ |
| Access governance files | ❌ | ❌ | ❌ |
| Access ledger | ❌ | ❌ | ✅ (write own events) |
| Store API credentials between sessions | ❌ | ❌ | ❌ |

### Under Vera

| Action / Resource | VRA-TKL-01 (Token Ledger) | VRA-MDL-01 (Model Router) | VRA-ROI-01 (ROI Scoring) |
|---|---|---|---|
| Read token_ledger | ✅ | ❌ | ❌ |
| Write token_ledger | ✅ | ❌ | ❌ |
| Read economic_metrics (budget limits) | ✅ (read only) | ❌ | ✅ |
| Write economic_metrics | ❌ | ❌ | ❌ |
| Read profit_equilibrium_formula | ❌ | ❌ | ✅ |
| Read Sorin's financial models | ❌ | ❌ | ✅ |
| Issue clearance decisions | ❌ (Vera decides) | ❌ | ❌ |
| Check local Ollama availability | ❌ | ✅ | ❌ |
| Read agent definitions | ❌ | ❌ | ❌ |

### Under Astra

| Action / Resource | AST-AUD-01 (Corpus Audit) | AST-CPD-01 (Change Proposal) | AST-DCL-01 (Doctrine Compliance) |
|---|---|---|---|
| Read all corpus files | ✅ | ✅ | ✅ |
| Write corpus files | ❌ | ❌ | ❌ |
| Scan for broken references | ✅ | ❌ | ✅ |
| Draft CP-XXXX documents | ❌ | ✅ | ❌ |
| Flag governance violations | ✅ | ✅ | ✅ |
| Read proposal packages | ❌ | ❌ | ✅ |
| Read execution plans | ❌ | ❌ | ✅ |
| Write ledger | ✅ (own events) | ✅ (own events) | ✅ (own events) |

---

## Tier 3 — Workers

| Worker | Read | Write | External Calls | Spawn Others | Ledger |
|--------|------|-------|----------------|--------------|--------|
| WRK-001 Web Scraper | URL content only | ❌ | HTTP GET to target URL | ❌ | ❌ |
| WRK-002 Keyword Extractor | Input text only | ❌ | ❌ | ❌ | ❌ |
| WRK-003 Link Validator | URL status only | ❌ | HTTP HEAD/GET to target | ❌ | ❌ |
| WRK-004 Email Formatter | Templates, input | ❌ | ❌ | ❌ | ❌ |
| WRK-005 HubSpot Field Updater | HubSpot object | HubSpot one field | HubSpot API PATCH | ❌ | ❌ |
| WRK-006 Ledger Entry | ❌ | audit_events (one row) | Workflow 05 webhook | ❌ | Write only |
| WRK-007 Cost Calculator | Pricing rates only | ❌ | ❌ | ❌ | ❌ |
| WRK-008 SHA Hash | Input string | ❌ | ❌ | ❌ | ❌ |
| WRK-009 Telegram Message | ❌ | ❌ | Telegram API | ❌ | ❌ |
| WRK-010 Data Parser | Input data | ❌ | ❌ | ❌ | ❌ |
| WRK-011 GitHub File Fetch | One repo file | ❌ | GitHub API GET | ❌ | ❌ |
| WRK-012 Venture Stage Updater | HubSpot deal | HubSpot stage field | HubSpot + Workflow 05 | ❌ | Write stage change |

**All workers:** No access to governance files, agent definitions, doctrine documents, or other agents' contexts.

---

## Escalation on Access Violation

If any agent or sub-agent attempts an unauthorized tool call:

1. `tool_policy.py` returns `AuthorizationResult(allowed=False)` with denial reason
2. The calling agent must not proceed with the tool call
3. A `TOOL_DENIED` audit event is emitted to the Ledger
4. If the attempt is from a Tier 2 or Tier 3 agent, the parent Council agent is notified
5. Repeated unauthorized tool attempts by the same agent trigger a HITL pause

Access violations are never silently swallowed. Every denial is logged.

---

## Credential Handling Rules

1. API keys and secrets are never stored in agent memory or corpus files
2. Credentials are passed to agents via environment variables at container start (`.env` file, not committed to git)
3. Sub-agents receive scoped credentials at spawn time from their parent — they do not hold them between sessions
4. Workers receive credentials as spawn parameters — never stored, always discarded after the task completes
5. `OPENAI_API_KEY`, `HEGEMON_AUDIT_WEBHOOK`, `HEGEMON_TOKEN_WEBHOOK` are environment variables only
6. All credential files (`.env`, `*.key`) are listed in `.gitignore` — committing secrets to the repo is a critical security violation

---

## Change Control

This matrix is updated only when the Architect approves an agent role change, new tool registration, or permission grant. All changes are submitted as Change Proposals (CP-XXXX) by Astra and require Architect approval before `tool_policy.py` is updated.
