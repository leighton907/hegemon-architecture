# Hegemon Workers Framework
**Version:** 1.0
**Status:** Active
**Authority:** Council Charter v2.6 — Tier 3

---

## Overview

Workers are the smallest unit of execution in Hegemon. They are single-purpose, stateless, and cheap to run. A Worker does **one thing**, returns a result, and terminates. Workers hold no memory between tasks and hold no session state. They are the anti-token-burn layer in action — high-volume, low-complexity work runs here at the lowest capable cost, preserving Council and sub-agent budgets for reasoning and judgment.

---

## Worker Laws

1. **One job.** A Worker has exactly one function. It does not branch, decide, or delegate.
2. **Stateless.** Workers hold no memory between spawns. Every spawn is fresh.
3. **Return or fail.** A Worker returns a result payload or returns a structured FAILURE. It never hangs silently.
4. **Cheapest capable model.** All Workers default to FREE tier (local Ollama) unless the task strictly requires API-tier reasoning. This must be justified in the spawn request.
5. **No self-escalation.** If a Worker encounters something outside its function, it returns OUT_OF_SCOPE to the spawning sub-agent. It does not attempt to handle it.
6. **Logged by parent.** Workers do not write to the Ledger directly. The spawning sub-agent or Council agent logs worker outcomes as part of their own audit trail.

---

## Spawn Protocol

Workers are spawned by Council agents or sub-agents. The spawn request must include:

```
worker_type: {worker_id from registry below}
task_id: {originating task reference}
spawned_by: {parent agent sim_id}
input: {structured input payload}
model_tier: FREE | ECONOMY (must be justified if ECONOMY)
timeout_seconds: {max runtime — default 30s}
```

The spawning agent is responsible for:
- Passing a complete, valid input payload
- Handling the returned result or FAILURE
- Logging the outcome as part of its own audit event

---

## Failure Response Format

Every Worker that fails returns:

```
worker_type: {worker_id}
status: FAILURE | TIMEOUT | OUT_OF_SCOPE
error: {brief description}
input_received: {echo of input for debugging}
timestamp: {ISO8601}
```

---

## Worker Registry

---

### WRK-001: Web Scraper Worker

**Function:** Fetches the content of a single URL and returns the raw text or structured HTML.
**Spawned By:** SRN-MRS-01 (Market Research Sub-Agent), BRM-INT-01 (Integration Sub-Agent)
**Model Tier:** FREE (Local Ollama or simple HTTP fetch — no LLM required for raw scraping)
**Timeout:** 15 seconds
**Concurrency:** Up to 20 simultaneous instances per sub-agent

**Input:**
```
url: {target URL}
output_format: raw_text | structured_html | json_extract
css_selector: {optional — for structured extraction}
```

**Output:**
```
url: {fetched URL}
status_code: {HTTP status}
content: {extracted text or structure}
content_length: {character count}
timestamp: {ISO8601}
```

**Forbidden:** Following redirects to unintended domains; storing content beyond return; executing JavaScript

---

### WRK-002: Keyword Extractor Worker

**Function:** Takes a block of text and returns a list of keywords, topics, and search-relevant phrases.
**Spawned By:** SRN-MRS-01 (Market Research Sub-Agent)
**Model Tier:** FREE (Local Ollama 7B sufficient)
**Timeout:** 20 seconds

**Input:**
```
text: {raw content block, max 10,000 characters}
focus: seo | topics | entities | all
max_keywords: {integer, default 20}
```

**Output:**
```
keywords: [{keyword, relevance_score}]
topics: [{topic, confidence}]
entities: [{entity, type}]
source_length: {character count of input}
```

---

### WRK-003: Link Validator Worker

**Function:** Checks that a URL is live, returns a valid status code, and optionally confirms a specific element is present.
**Spawned By:** BRM-INT-01 (Integration Sub-Agent)
**Model Tier:** FREE (HTTP check — no LLM)
**Timeout:** 10 seconds

**Input:**
```
url: {URL to validate}
expected_status: {integer, default 200}
check_element: {optional CSS selector or text string to confirm presence}
```

**Output:**
```
url: {checked URL}
status_code: {actual HTTP status}
is_live: {boolean}
element_found: {boolean if check_element provided}
response_time_ms: {integer}
```

---

### WRK-004: Email Template Formatter Worker

**Function:** Takes raw text content and wraps it in the appropriate HTML email template for the specified email type.
**Spawned By:** RXY-COM-01 (Comms Formatting Sub-Agent), directly by Brom
**Model Tier:** ECONOMY (Haiku — template application with variable injection)
**Timeout:** 15 seconds

**Input:**
```
content: {raw text or markdown}
email_type: ALERT | REPORT | NOTIFICATION | ESCALATION
recipient_name: {string}
task_id: {optional reference}
sender_agent: {string}
```

**Output:**
```
subject: {generated subject line}
html_body: {complete HTML email body}
plain_text_body: {plain text fallback}
email_type: {echo of input type}
```

**Forbidden:** Altering factual content; adding links not present in source material

---

### WRK-005: HubSpot Field Updater Worker

**Function:** Updates one specific field in a HubSpot object (Contact, Company, Deal, or Note).
**Spawned By:** BRM-INT-01 (Integration Sub-Agent), Brom directly
**Model Tier:** FREE (API call — no LLM)
**Timeout:** 10 seconds

**Input:**
```
object_type: CONTACT | COMPANY | DEAL | NOTE
object_id: {HubSpot object ID}
field_name: {property name}
field_value: {new value}
hubspot_api_key: {passed at spawn, not stored}
```

**Output:**
```
object_id: {updated object ID}
field_name: {updated field}
previous_value: {prior value if retrievable}
new_value: {confirmed new value}
status: SUCCESS | FAILURE
```

---

### WRK-006: Ledger Entry Worker

**Function:** Writes a single audit event to the `audit_events` table via the `/hegemon-audit-log` webhook.
**Spawned By:** Any Council agent or sub-agent
**Model Tier:** FREE (webhook POST — no LLM)
**Timeout:** 5 seconds

**Input:**
```
event_id: {string}
actor: {agent sim_id}
action: {action description}
outcome: SUCCESS | FAILURE | PENDING | BLOCKED
details: {object}
task_id: {optional}
timestamp: {ISO8601}
```

**Output:**
```
event_id: {confirmed}
integrity_hash: {SHA256 returned by Workflow 05}
status: LOGGED | FAILED
```

**Note:** This worker wraps Workflow 05. It must never fail silently — if the Ledger is unreachable, it returns FAILURE immediately so the spawning agent can retry.

---

### WRK-007: Cost Calculator Worker

**Function:** Takes token count and model type, returns the cost in USD.
**Spawned By:** Vera, VRA-TKL-01 (Token Ledger Sub-Agent)
**Model Tier:** FREE (arithmetic — no LLM)
**Timeout:** 2 seconds

**Input:**
```
model_tier: PREMIUM | STANDARD | ECONOMY | FREE
tokens_input: {integer}
tokens_output: {integer}
```

**Output:**
```
model_tier: {echo}
cost_input_usd: {float}
cost_output_usd: {float}
total_cost_usd: {float}
```

**Rates (placeholder — updated via Vera's economic_metrics):**
- PREMIUM (Opus): $0.015/1K in, $0.075/1K out
- STANDARD (Sonnet): $0.003/1K in, $0.015/1K out
- ECONOMY (Haiku): $0.00025/1K in, $0.00125/1K out
- FREE (Local): $0.00

---

### WRK-008: SHA Hash Worker

**Function:** Generates a SHA256 integrity hash for a given payload string.
**Spawned By:** Brom (for execution records), Workflow 05 (internally)
**Model Tier:** FREE (cryptographic function — no LLM)
**Timeout:** 2 seconds

**Input:**
```
payload: {string to hash — typically concatenated key fields}
```

**Output:**
```
hash: {SHA256 hex string}
payload_length: {character count of input}
```

---

### WRK-009: Telegram Message Worker

**Function:** Sends one formatted message to one Telegram chat ID via Workflow 02's outbound webhook.
**Spawned By:** RXY-COM-01 (Comms Formatting Sub-Agent), Brom, Vera
**Model Tier:** FREE (webhook POST — no LLM)
**Timeout:** 10 seconds

**Input:**
```
chat_id: {Telegram chat ID}
message: {pre-formatted message string, max 4096 characters}
task_id: {optional reference}
```

**Output:**
```
chat_id: {confirmed}
message_id: {Telegram-assigned message ID}
status: SENT | FAILED
timestamp: {ISO8601}
```

---

### WRK-010: Data Parser Worker

**Function:** Takes raw structured data (JSON, CSV, HTML table) and normalizes it into a clean JSON object matching a specified schema.
**Spawned By:** SRN-MRS-01 (Market Research Sub-Agent), BRM-INT-01 (Integration Sub-Agent)
**Model Tier:** FREE (Local Ollama 7B — pattern matching and transformation)
**Timeout:** 30 seconds

**Input:**
```
raw_data: {string — JSON, CSV, or HTML}
input_format: json | csv | html_table
target_schema: {JSON schema definition}
```

**Output:**
```
parsed_data: {JSON object matching target_schema}
fields_mapped: {integer}
fields_missing: [{field names not found in source}]
parse_confidence: HIGH | MEDIUM | LOW
```

---

### WRK-011: GitHub File Fetch Worker

**Function:** Fetches the contents of a specific file from the Hegemon GitHub repository.
**Spawned By:** Astra's Corpus Audit Sub-Agent, Brom
**Model Tier:** FREE (GitHub API GET — no LLM)
**Timeout:** 10 seconds

**Input:**
```
repo_owner: {GitHub username}
repo_name: {repository name}
file_path: {path within repo}
github_token: {passed at spawn, not stored}
branch: {default: main}
```

**Output:**
```
file_path: {confirmed}
content: {decoded file content}
sha: {file SHA for change detection}
last_modified: {ISO8601}
```

---

### WRK-012: Venture Stage Updater Worker

**Function:** Updates a venture's stage in HubSpot and logs the stage change to the Ledger. Combines WRK-005 and WRK-006 for the common venture tracking operation.
**Spawned By:** Brom, BRM-INT-01
**Model Tier:** FREE (two API calls — no LLM)
**Timeout:** 15 seconds

**Input:**
```
venture_name: {string}
hubspot_deal_id: {HubSpot Deal object ID}
new_stage: DESIGN | DESIGN_APPROVED | IN_PROGRESS | ACTIVE | PAUSED | CLOSED
task_id: {originating task}
hubspot_api_key: {passed at spawn}
```

**Output:**
```
venture_name: {confirmed}
previous_stage: {prior value}
new_stage: {confirmed new stage}
hubspot_updated: {boolean}
ledger_logged: {boolean}
status: SUCCESS | PARTIAL | FAILURE
```

---

## Worker Concurrency Limits

| Spawning Agent | Max Concurrent Workers |
|----------------|------------------------|
| SRN-MRS-01 (Market Research) | 20 |
| BRM-INT-01 (Integration) | 10 |
| BRM-INF-01 (Infrastructure) | 5 |
| Any Council agent directly | 10 |
| Any other sub-agent | 5 |

Limits are enforced by the spawning agent. Vera monitors for anomalous worker spawning patterns via the Token Ledger Sub-Agent.

---

## Adding New Workers

New worker types may only be added via a formal Change Proposal (CP-XXXX) submitted by Astra and approved by the Architect. The proposal must define: worker function, spawn authority, model tier justification, input/output schema, timeout, concurrency limit, and forbidden actions.
