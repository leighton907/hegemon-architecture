"""
Council authority check: verifies actor is allowed to invoke required_role.
Used by Roxy router before economic and execution gates.
"""

COUNCIL_ROLES = ("RXY-CEO", "SRN-CFO", "BRM-CTO")


def verify_authority(actor: str, required_role: str) -> bool:
    """
    Return True if actor may invoke the required_role.
    RXY-CEO may request any role; others may only request their own role.
    """
    if required_role not in COUNCIL_ROLES:
        return False
    if actor == "RXY-CEO":
        return True
    return actor == required_role
