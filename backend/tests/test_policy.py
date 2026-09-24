import pytest
from app.policy.permissions import determine_approval_route
from app.policy.engine import policy_engine
from app.models.recommendation import ActionRecommendation

def test_approval_routing():
    assert determine_approval_route("ALLOW_TRANSACTION") == "auto"
    assert determine_approval_route("CREATE_CASE") == "auto"
    assert determine_approval_route("DECLINE_TRANSACTION") == "L1"
    assert determine_approval_route("BLOCK_CARD", exposure_usd=500.0) == "L1"
    assert determine_approval_route("BLOCK_CARD", exposure_usd=3000.0) == "L2"
    assert determine_approval_route("BLOCK_ALL_CARDS") == "L2"
    assert determine_approval_route("FILE_REPORT") == "L2"

def test_rule_r1_weak_signal():
    ctx = {
        "single_signal": True,
        "fraud_probability": 0.61,
        "customer_response": None
    }
    recs = policy_engine.evaluate(ctx)
    action_names = [r.action for r in recs]
    assert "VERIFY_WITH_CUSTOMER" in action_names

def test_rule_r2_customer_denial():
    ctx = {
        "customer_response": "denied",
        "exposure_usd": 1500.0,
        "fraud_probability": 0.86
    }
    recs = policy_engine.evaluate(ctx)
    action_names = [r.action for r in recs]
    assert "BLOCK_CARD" in action_names
    assert "CREATE_CASE" in action_names
    assert "FILE_REPORT" in action_names

def test_rule_r3_customer_confirmation():
    ctx = {
        "customer_response": "confirmed",
        "fraud_probability": 0.10
    }
    recs = policy_engine.evaluate(ctx)
    action_names = [r.action for r in recs]
    assert "CLOSE_NO_FRAUD" in action_names

def test_rule_r5_card_testing():
    ctx = {
        "is_card_testing": True,
        "cleared_purchase_over_100": False,
        "fraud_probability": 0.72
    }
    recs = policy_engine.evaluate(ctx)
    action_names = [r.action for r in recs]
    assert "DECLINE_TRANSACTION" in action_names
    assert "STEP_UP_AUTH" in action_names

def test_rule_r10_block_all_cards_restriction():
    ctx = {
        "confirmed_fraud_card_count": 1,
        "credentials_compromised": False
    }

    # Attempt to inject BLOCK_ALL_CARDS manually into rules
    raw_actions = [
        ActionRecommendation(action="BLOCK_ALL_CARDS", route="L2", reason="Attempted block all")
    ]
    from app.policy.rules import PolicyRules
    filtered = PolicyRules.enforce_r10(raw_actions, ctx)
    assert len(filtered) == 0  # Blocked by R10
