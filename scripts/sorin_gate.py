"""
Financial governance gate: Sorin (CFO) economic approval logic.
All operations with estimated cost must pass here before execution.
"""
from ledger_writer import log_event

LOW_COST = 5000
MEDIUM_COST = 20000
HIGH_COST = 50000


def approve_cost(actor: str, estimated_tokens: int, action: str) -> bool:
    """
    Gate estimated token cost. Returns True if execution allowed, False if denied.
    Logs to audit ledger with SRN-CFO and appropriate action/details.
    """
    details_base = f"actor={actor} action={action} tokens={estimated_tokens}"

    if estimated_tokens <= LOW_COST:
        log_event(
            actor="SRN-CFO",
            action="cost_auto_approved",
            details=details_base,
        )
        return True

    if estimated_tokens <= MEDIUM_COST:
        log_event(
            actor="SRN-CFO",
            action="cost_review_required",
            details=details_base,
        )
        return True

    if estimated_tokens <= HIGH_COST:
        log_event(
            actor="SRN-CFO",
            action="cost_denied",
            details=f"{details_base} CFO_REVIEW_REQUIRED",
        )
        return False

    log_event(
        actor="SRN-CFO",
        action="cost_blocked",
        details=f"{details_base} COST_BLOCKED",
    )
    return False


if __name__ == "__main__":
    for tokens in [1000, 15000, 60000]:
        allowed = approve_cost(actor="test_actor", estimated_tokens=tokens, action="test_run")
        print(f"{tokens} tokens -> approved: {allowed}")
