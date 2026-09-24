from typing import List, Dict, Any
from app.models.recommendation import ActionRecommendation, NextBestActions
from app.policy.rules import PolicyRules
from app.policy.permissions import determine_approval_route

class FraudPolicyEngine:
    """
    Deterministic Fraud Policy Engine implementing Fraud Policy v1.0.
    Evaluates rules R1 to R10 and enforces approval routing (auto, L1, L2).
    """

    def evaluate(self, context: Dict[str, Any]) -> List[ActionRecommendation]:
        actions: List[ActionRecommendation] = []

        # R1: Weak signal verify
        actions.extend(PolicyRules.evaluate_r1(context))

        # R2: Customer denial
        actions.extend(PolicyRules.evaluate_r2(context))

        # R3: Customer confirmation
        actions.extend(PolicyRules.evaluate_r3(context))

        # R4: No reply 24h
        actions.extend(PolicyRules.evaluate_r4(context))

        # R5: Card testing
        actions.extend(PolicyRules.evaluate_r5(context))

        # R6: Shared origin
        actions.extend(PolicyRules.evaluate_r6(context))

        # R7: Disputed recurring
        actions.extend(PolicyRules.evaluate_r7(context))

        # R8: Escalate when uncertain & exposed
        actions.extend(PolicyRules.evaluate_r8(context))

        # R9: Undocumented pattern
        actions.extend(PolicyRules.evaluate_r9(context))

        # Fallback if no rules matched and probability > 0.30
        prob = context.get("fraud_probability", 0.0)
        verdict = context.get("verdict", "legitimate")
        if not actions:
            if verdict == "legitimate" and prob <= 0.30:
                actions.append(ActionRecommendation(
                    action="ALLOW_TRANSACTION",
                    route=determine_approval_route("ALLOW_TRANSACTION"),
                    reason="Low risk score/fraud probability; allow transaction to stand."
                ))
            elif prob >= 0.30:
                actions.append(ActionRecommendation(
                    action="CREATE_CASE",
                    route=determine_approval_route("CREATE_CASE"),
                    reason="R3a: Open internal case as fraud probability reaches 0.30."
                ))

        # Enforce R10 guard rule
        actions = PolicyRules.enforce_r10(actions, context)

        # Deduplicate actions preserving order
        seen = set()
        deduped = []
        for act in actions:
            if act.action not in seen:
                seen.add(act.action)
                deduped.append(act)

        return deduped

    def generate_next_best_actions(
        self,
        initial_context: Dict[str, Any],
        final_context: Dict[str, Any],
        what_changed_reason: str = "nothing"
    ) -> NextBestActions:
        initial_recs = self.evaluate(initial_context)
        final_recs = self.evaluate(final_context)

        # Determine what_changed text if not explicitly supplied
        if initial_recs == final_recs and what_changed_reason == "nothing":
            what_changed = "nothing"
        else:
            what_changed = what_changed_reason

        return NextBestActions(
            initial=initial_recs,
            final=final_recs,
            what_changed=what_changed
        )

policy_engine = FraudPolicyEngine()
