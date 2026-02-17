"""
Primary reasoning router for Hegemon.
Roxy evaluates requests and routes through governance and economic checks.
Does NOT execute actions.
"""
from council_authority import verify_authority
from sorin_gate import approve_cost
from ledger_writer import log_event


def _required_role(request: str) -> str:
    """Determine required council role from request keywords."""
    r = request.lower()
    if any(k in r for k in ("finance", "budget", "cost")):
        return "SRN-CFO"
    if any(k in r for k in ("architecture", "system", "deploy")):
        return "BRM-CTO"
    return "RXY-CEO"


def process_request(actor: str, request: str, estimated_tokens: int) -> str:
    """
    Evaluate request: log start, check authority, check cost, return status.
    Returns: APPROVED_FOR_EXECUTION | DENIED_AUTHORITY | DENIED_COST
    """
    log_event(
        actor="RXY-CEO",
        action="reasoning_started",
        details=request,
    )

    required_role = _required_role(request)

    if not verify_authority(actor, required_role):
        log_event(
            actor="RXY-CEO",
            action="authority_failed",
            details=request,
        )
        return "DENIED_AUTHORITY"

    if not approve_cost(actor, estimated_tokens, request):
        log_event(
            actor="RXY-CEO",
            action="economic_denied",
            details=request,
        )
        return "DENIED_COST"

    log_event(
        actor="RXY-CEO",
        action="request_approved",
        details=request,
    )
    return "APPROVED_FOR_EXECUTION"


if __name__ == "__main__":
    tests = [
        ("check system architecture", 3000),
        ("run financial audit", 10000),
        ("execute unknown task", 1000),
    ]
    for request, tokens in tests:
        result = process_request(actor="RXY-CEO", request=request, estimated_tokens=tokens)
        print(f"{request!r} ({tokens} tokens) -> {result}")
