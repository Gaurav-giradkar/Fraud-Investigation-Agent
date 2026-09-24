from typing import List, Dict, Any
from app.models.recommendation import ActionRecommendation
from app.policy.permissions import determine_approval_route

class PolicyRules:

    @staticmethod
    def evaluate_r1(context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R1: Verify before block on weak signal."""
        actions = []
        single_signal = context.get("single_signal", False)
        prob = context.get("fraud_probability", 0.0)
        customer_response = context.get("customer_response")

        if single_signal and prob < 0.70 and not customer_response:
            actions.append(ActionRecommendation(
                action="VERIFY_WITH_CUSTOMER",
                route=determine_approval_route("VERIFY_WITH_CUSTOMER"),
                reason=f"R1: Single signal with fraud probability {prob:.2f} (< 0.70), verify before blocking."
            ))
        return actions

    @staticmethod
    def evaluate_r2(context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R2: Customer denies transaction."""
        actions = []
        customer_response = context.get("customer_response")
        exposure = context.get("exposure_usd", 0.0)
        shared_origin = context.get("has_shared_origin", False)

        if customer_response == "denied":
            route_block = determine_approval_route("BLOCK_CARD", exposure)
            actions.append(ActionRecommendation(
                action="BLOCK_CARD",
                route=route_block,
                reason=f"R2: Customer denied transaction. Exposure is ${exposure:.2f}."
            ))
            actions.append(ActionRecommendation(
                action="CREATE_CASE",
                route=determine_approval_route("CREATE_CASE"),
                reason="R2: Customer dispute requires opening an internal case."
            ))
            if exposure > 1000.0 or shared_origin:
                actions.append(ActionRecommendation(
                    action="FILE_REPORT",
                    route=determine_approval_route("FILE_REPORT"),
                    reason="R2: Exposure exceeds $1,000 or activity connects to a shared device/card."
                ))
        return actions

    @staticmethod
    def evaluate_r3(context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R3: Customer confirms transaction."""
        actions = []
        if context.get("customer_response") == "confirmed":
            actions.append(ActionRecommendation(
                action="CLOSE_NO_FRAUD",
                route=determine_approval_route("CLOSE_NO_FRAUD"),
                reason="R3: Customer confirmed transaction as legitimate."
            ))
        return actions

    @staticmethod
    def evaluate_r4(context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R4: No reply within 24 hours."""
        actions = []
        exposure = context.get("exposure_usd", 0.0)
        if context.get("customer_response") == "no_reply":
            actions.append(ActionRecommendation(
                action="MONITOR_CARD",
                route=determine_approval_route("MONITOR_CARD"),
                reason="R4: No customer response within 24 hours, place card on monitoring."
            ))
            actions.append(ActionRecommendation(
                action="DECLINE_TRANSACTION",
                route=determine_approval_route("DECLINE_TRANSACTION"),
                reason="R4: Decline pending authorizations due to unconfirmed activity."
            ))
            if exposure > 500.0:
                actions.append(ActionRecommendation(
                    action="ESCALATE_TO_ANALYST",
                    route=determine_approval_route("ESCALATE_TO_ANALYST"),
                    reason="R4: Escalate to analyst because exposure exceeds $500."
                ))
        return actions

    @staticmethod
    def evaluate_r5(context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R5: Card testing."""
        actions = []
        exposure = context.get("exposure_usd", 0.0)
        if context.get("is_card_testing"):
            cleared_over_100 = context.get("cleared_purchase_over_100", False)
            if cleared_over_100:
                route_block = determine_approval_route("BLOCK_CARD", exposure)
                actions.append(ActionRecommendation(
                    action="BLOCK_CARD",
                    route=route_block,
                    reason="R5: Card testing observed and purchase over $100 has cleared."
                ))
            else:
                actions.append(ActionRecommendation(
                    action="DECLINE_TRANSACTION",
                    route=determine_approval_route("DECLINE_TRANSACTION"),
                    reason="R5: Testing sequence observed, decline pending transaction."
                ))
                actions.append(ActionRecommendation(
                    action="STEP_UP_AUTH",
                    route=determine_approval_route("STEP_UP_AUTH"),
                    reason="R5: Require step-up auth for testing sequence."
                ))
        return actions

    @staticmethod
    def evaluate_r6(context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R6: Shared origin across cards/devices."""
        actions = []
        if context.get("has_shared_origin"):
            actions.append(ActionRecommendation(
                action="CREATE_CASE",
                route=determine_approval_route("CREATE_CASE"),
                reason="R6: Shared device profile/region/email origin detected."
            ))
            actions.append(ActionRecommendation(
                action="FILE_REPORT",
                route=determine_approval_route("FILE_REPORT"),
                reason="R6: Coordinated fraud across shared origin elements."
            ))
            actions.append(ActionRecommendation(
                action="MONITOR_CONNECTED_CARDS",
                route=determine_approval_route("MONITOR_CONNECTED_CARDS"),
                reason="R6: Monitor all cards sharing the origin element."
            ))
        return actions

    @staticmethod
    def evaluate_r7(context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R7: Disputed recurring charge."""
        actions = []
        if context.get("is_disputed_recurring"):
            actions.append(ActionRecommendation(
                action="CREATE_CASE",
                route=determine_approval_route("CREATE_CASE"),
                reason="R7: Disputed recurring merchant transaction."
            ))
            actions.append(ActionRecommendation(
                action="VERIFY_WITH_CUSTOMER",
                route=determine_approval_route("VERIFY_WITH_CUSTOMER"),
                reason="R7: Verify recurring subscription with customer."
            ))
            actions.append(ActionRecommendation(
                action="WARN_CUSTOMER",
                route=determine_approval_route("WARN_CUSTOMER"),
                reason="R7: Send informational message regarding recurring billing rules."
            ))
        return actions

    @staticmethod
    def evaluate_r8(context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R8: Escalate when uncertain and exposed."""
        actions = []
        verdict = context.get("verdict")
        exposure = context.get("exposure_usd", 0.0)
        if verdict == "uncertain" and (exposure > 500.0 or context.get("conflicting_evidence")):
            actions.append(ActionRecommendation(
                action="ESCALATE_TO_ANALYST",
                route=determine_approval_route("ESCALATE_TO_ANALYST"),
                reason=f"R8: Verdict is uncertain and exposure is ${exposure:.2f} (> $500)."
            ))
        return actions

    @staticmethod
    def evaluate_r9(context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R9: Undocumented pattern."""
        actions = []
        if context.get("is_undocumented"):
            actions.append(ActionRecommendation(
                action="CREATE_CASE",
                route=determine_approval_route("CREATE_CASE"),
                reason="R9: Open case for undocumented pattern."
            ))
            actions.append(ActionRecommendation(
                action="FILE_REPORT",
                route=determine_approval_route("FILE_REPORT"),
                reason="R9: File report for coordinated/repeated undocumented pattern."
            ))
            actions.append(ActionRecommendation(
                action="ESCALATE_TO_ANALYST",
                route=determine_approval_route("ESCALATE_TO_ANALYST"),
                reason="R9: Escalate undocumented fraud pattern to analyst for review."
            ))
        return actions

    @staticmethod
    def enforce_r10(actions: List[ActionRecommendation], context: Dict[str, Any]) -> List[ActionRecommendation]:
        """R10: BLOCK_ALL_CARDS restrictions."""
        confirmed_cards = context.get("confirmed_fraud_card_count", 0)
        creds_compromised = context.get("credentials_compromised", False)

        filtered = []
        for act in actions:
            if act.action == "BLOCK_ALL_CARDS":
                if confirmed_cards >= 2 or creds_compromised:
                    filtered.append(act)
            else:
                filtered.append(act)
        return filtered
