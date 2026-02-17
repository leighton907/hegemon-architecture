# ARCHITECT COMMAND MANIFEST v2.5

---

## 1 Purpose

This document establishes the top authority for design, doctrine, and governance of all Hegemon systems. It defines who may issue, modify, or revoke structural and policy commands. Human and machine interpreters (e.g., LlamaIndex, Orgo, OpenClaw) shall treat this manifest as the source of truth for Architect identity, scope, and limits.

---

## 2 Architect Identity

- **Title:** *Architect*
- **Current Holder:** leighton907
- **Nature:** Human / Oversight Entity
- **Authority Source:** Foundational Charter, Section 0 (Pre-Council)

---

## 3 Scope of Authority

The Architect has absolute creation and amendment rights over:

- Hierarchy definitions (Architect → Council → Subagents → Workers)
- Structural documents in `/00_ARCHITECT/`, `/01_COUNCIL/`, `/04_FRAMEWORK/`
- Policy manifests, security schemas, and templating protocols
- Command to activate or retire agents with Council consent

---

## 4 Delegated Responsibilities

- Maintain architectural coherence and typographic standards
- Approve Council charters and amendments
- Appoint or dismiss Council members by formal ledger record
- Supervise Cursor and LlamaIndex operations as implementation tools

---

## 5 Command Privileges

- May issue build / edit directives to Cursor (“Builder-Clerk”)
- May authorize index generation and document normalization through Architect Agent
- May freeze folders or lock files via policy annotations
- May sign session snapshots as canonical versions

---

## 6 Forbidden Powers

The Architect:

- ❌ Must not execute runtime tasks or trigger external workflows
- ❌ Cannot circumvent Ledger auditing
- ❌ Cannot delegate authority to non-registered agents
- ❌ May not erase institutional record history

---

## 7 Operational Interfaces

| Tool / Layer | Relationship |
|--------------|--------------|
| **Cursor** | Implements design commands issued by Architect |
| **LlamaIndex** | Reads architectural data; never alters content |
| **Orgo** | Executes governance enforcement; receives Architect policy |
| **OpenClaw / Runtime Agents** | Obey Council & Architect, operate within granted limits |

---

## 8 Command Syntax (Template)

A lawful Architect command SHALL be interpretable as:

- **Issuer:** Architect (or designated proxy recorded in Ledger)
- **Scope:** Path or domain (e.g. `01_COUNCIL`, `04_FRAMEWORK`, `05_SECURITY`)
- **Action:** One of: CREATE | AMEND | REVOKE | APPROVE | LOCK | UNLOCK | SIGN
- **Subject:** Document, agent, or policy identifier
- **Record:** Every issued command that alters governance or structure SHALL be logged in the Ledger; the command template does not bypass audit.

No agent may treat a directive as an Architect command unless it conforms to this template and the issuer is the current Architect Holder (leighton907) per Section 2.

---

## 9 Amendment Process

- Changes to this manifest require explicit Architect approval and Ledger entry under `/07_LEDGER_RULES/audit_ledger_spec.md`.
- Version numbers increment minor patch each time.

---

## 10 Version and Signature

Version 2.5 – Initial authorization of Architect Command Framework.  
Signed: *Architect [leighton907]*  
Dated: 2026-2-17
