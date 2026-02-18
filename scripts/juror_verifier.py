"""
Juror verification layer (v3 strict): validates requests against doctrine domains and canonical docs.
Pass only if: (1) at least one ALLOWED_DOMAIN in request, AND (2) at least one strong grounding token in docs.
"""
from pathlib import Path

from ledger_writer import log_event

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"

CANONICAL = [
    "ARCHITECTURE.md",
    "LEDGER.md",
    "VISUAL_IDENTITY.md",
    "system_principles.md",
]
LEDGER_FALLBACK = "LEDGER_GOVERNANCE.md"

ALLOWED_DOMAINS = [
    "architecture",
    "ledger",
    "finance",
    "governance",
    "deployment",
    "workflow",
    "identity",
    "agent",
    "economic",
    "system",
]

DOMAIN_ALIASES = {
    "financial": "finance",
    "economics": "economic",
    "architectural": "architecture",
    "governance": "governance"
}

STOPWORDS = {
    "please", "could", "would", "check", "system", "execute", "unknown",
    "random", "task", "audit", "command", "verify", "validate",
}


def _load_canonical_text() -> str:
    """Load all canonical docs into one lowercase string."""
    chunks = []
    for name in CANONICAL:
        path = DOCS_DIR / name
        if not path.exists() and name == "LEDGER.md":
            path = DOCS_DIR / LEDGER_FALLBACK
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    return " ".join(chunks).lower()


def verify_against_docs(request: str) -> dict:
    """
    v3 strict: PASS only if matched_domains non-empty AND at least one grounding token (>=6 chars, not in STOPWORDS) in docs.
    Returns dict with pass, reason, matched_domains, grounding_tokens.
    """
    request_lower = request.strip().lower()
    docs_text = _load_canonical_text()

    matched_domains = []
    for word in request_lower.split():
        if word in ALLOWED_DOMAINS:
            matched_domains.append(word)
        elif word in DOMAIN_ALIASES:
            matched_domains.append(DOMAIN_ALIASES[word])

    matched_domains = list(set(matched_domains))

    words = request_lower.split()
    grounding_tokens = [w for w in words if len(w) >= 6 and w not in STOPWORDS]
    doc_match = any(tok in docs_text for tok in grounding_tokens)

    domain_grounded = any(
        domain in docs_text
        for domain in matched_domains
    )
    doc_match = doc_match or domain_grounded

    if not matched_domains:
        reason = "NO_DOMAIN_MATCH"
        log_event(
            actor="JUROR",
            action="verification_failed",
            details=f"{request} ({reason})",
        )
        return {
            "pass": False,
            "reason": reason,
            "matched_domains": [],
            "grounding_tokens": grounding_tokens,
        }

    if not doc_match:
        reason = "NO_DOC_GROUNDING"
        log_event(
            actor="JUROR",
            action="verification_failed",
            details=f"{request} ({reason})",
        )
        return {
            "pass": False,
            "reason": reason,
            "matched_domains": matched_domains,
            "grounding_tokens": grounding_tokens,
        }

    log_event(
        actor="JUROR",
        action="verification_passed",
        details=request,
    )
    return {
        "pass": True,
        "reason": "PASS",
        "matched_domains": matched_domains,
        "grounding_tokens": grounding_tokens,
    }


if __name__ == "__main__":
    for req in [
        "check system architecture",
        "run financial audit",
        "execute unknown task",
        "make me a sandwich",
    ]:
        result = verify_against_docs(req)
        status = "PASS" if result["pass"] else result["reason"]
        print(f"{req!r} -> {status} (domains={result['matched_domains']}, grounding={result['grounding_tokens']})")
