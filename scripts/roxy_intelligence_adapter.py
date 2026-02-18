"""
Intelligence adapter for Hegemon.
Single facade for intent classification and doc grounding used by the reasoning router (Roxy).
Deterministic today; pluggable for future external intelligence (e.g. LLM).
"""
from intent_classifier import classify_intent
from juror_verifier import verify_against_docs
from ledger_writer import log_event


def get_intelligence(request: str) -> dict:
    """
    Return combined intelligence for a request: intent classification and juror grounding.
    Keys: intent, intent_confidence, juror_pass, juror_reason, matched_domains, grounding_tokens.
    """
    request_stripped = request.strip()
    intent_result = classify_intent(request_stripped)
    juror_result = verify_against_docs(request_stripped)

    out = {
        "intent": intent_result["intent"],
        "intent_confidence": intent_result["confidence"],
        "juror_pass": juror_result["pass"],
        "juror_reason": juror_result["reason"],
        "matched_domains": juror_result["matched_domains"],
        "grounding_tokens": juror_result["grounding_tokens"],
    }

    log_event(
        actor="INTELLIGENCE_ADAPTER",
        action="intelligence_computed",
        details=f"{request_stripped[:80]} -> intent={out['intent']} juror={out['juror_reason']}",
    )
    return out


if __name__ == "__main__":
    for req in [
        "check system architecture",
        "run financial audit",
        "execute unknown task",
        "make me a sandwich",
    ]:
        result = get_intelligence(req)
        status = "PASS" if result["juror_pass"] else result["juror_reason"]
        print(f"{req!r}")
        print(f"  intent={result['intent']} | juror={status} | domains={result['matched_domains']}")
