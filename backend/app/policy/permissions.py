from app.models.recommendation import ApprovalRoute

VALID_ACTIONS = {
    "ALLOW_TRANSACTION",
    "DECLINE_TRANSACTION",
    "MONITOR_CARD",
    "MONITOR_CONNECTED_CARDS",
    "WARN_CUSTOMER",
    "VERIFY_WITH_CUSTOMER",
    "STEP_UP_AUTH",
    "BLOCK_CARD",
    "BLOCK_ALL_CARDS",
    "GENERATE_REPORT",
    "CREATE_CASE",
    "FILE_REPORT",
    "ESCALATE_TO_ANALYST",
    "CLOSE_NO_FRAUD",
}

AUTO_ACTIONS = {
    "ALLOW_TRANSACTION",
    "MONITOR_CARD",
    "MONITOR_CONNECTED_CARDS",
    "WARN_CUSTOMER",
    "VERIFY_WITH_CUSTOMER",
    "STEP_UP_AUTH",
    "GENERATE_REPORT",
    "CREATE_CASE",
    "ESCALATE_TO_ANALYST",
    "CLOSE_NO_FRAUD",
}

def determine_approval_route(action: str, exposure_usd: float = 0.0) -> ApprovalRoute:
    """
    Determines approval route based on Fraud Policy Section 2:
    - auto: ALLOW_TRANSACTION, MONITOR_CARD, MONITOR_CONNECTED_CARDS, WARN_CUSTOMER,
            VERIFY_WITH_CUSTOMER, STEP_UP_AUTH, GENERATE_REPORT, CREATE_CASE,
            ESCALATE_TO_ANALYST, CLOSE_NO_FRAUD
    - L1 (team lead): DECLINE_TRANSACTION; BLOCK_CARD when exposure <= $2,500
    - L2 (fraud manager): BLOCK_CARD when exposure > $2,500; BLOCK_ALL_CARDS always; FILE_REPORT always
    """
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid policy action: '{action}'. Must be one of {VALID_ACTIONS}")

    if action in AUTO_ACTIONS:
        return "auto"

    if action == "DECLINE_TRANSACTION":
        return "L1"

    if action == "BLOCK_CARD":
        return "L1" if exposure_usd <= 2500.0 else "L2"

    if action in ("BLOCK_ALL_CARDS", "FILE_REPORT"):
        return "L2"

    return "auto"
