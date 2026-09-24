FRAUD_PATTERN_ANALYSIS_PROMPT = """
You are an expert fraud investigation analyst.
Analyze the following evidence for Case {case_id}:
- Flagged Transaction: {flagged_txn}
- Trigger Text: {trigger_text}
- Customer ID: {customer_id}, Card ID: {card_id}
- Collected Evidence: {evidence_summary}
- Historical Prior Cases: {prior_cases_summary}

Determine the most likely fraud pattern among:
1. card_testing
2. card_not_present_fraud
3. card_not_present_new_device
4. out_of_region_use
5. account_takeover
6. undocumented
7. none

Return your reasoning and conclusion.
"""

SAR_NARRATIVE_PROMPT = """
Write a complete, professional Suspicious Activity Report (SAR) narrative adhering to FinCEN guidelines.
The narrative must state:
- WHO: Customer {customer_id}, Card {card_id}, connected entities {subjects}
- WHAT: Fraud pattern {pattern}, exposure ${exposure_usd}
- WHEN: Dates {activity_dates}
- WHERE: Channels and billing regions
- HOW: Method of compromise or testing
- WHY: Why the activity is suspicious

The narrative must be 6 to 12 concise, factual sentences that stand on their own.
"""
