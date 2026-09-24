from typing import List, Dict, Any, Optional, TypedDict

class EvidenceRequestDict(TypedDict):
    type: str  # customer_validation | step_up_auth | analyst_info
    asked_after_step: int
    assumed_response: str

class ActionRecommendationDict(TypedDict):
    action: str
    route: str
    reason: str

class SARDict(TypedDict):
    file: bool
    reason: str
    narrative: str
    subjects: List[str]
    total_amount_usd: float
    activity_dates: List[str]

class InvestigationState(TypedDict, total=False):
    case_id: str
    opened_at: str
    trigger_type: str
    trigger_text: str
    flagged_txn_id: str
    card_id: str
    customer_id: str
    risk_score: Optional[float]

    flagged_transaction: Optional[Dict[str, Any]]
    graph_evidence: List[Dict[str, Any]]
    similar_prior_cases: List[str]
    
    pattern: str
    pattern_description: str
    verdict: str  # fraud | legitimate | uncertain
    status: str   # open | closed_fraud | closed_legitimate | escalated
    fraud_probability: float
    
    affected_txn_ids: List[str]
    first_suspicious_txn_id: str
    connected_card_ids: List[str]
    connected_device_profiles: List[str]
    exposure_usd: float
    
    evidence_requests: List[EvidenceRequestDict]
    initial_actions: List[ActionRecommendationDict]
    final_actions: List[ActionRecommendationDict]
    what_changed: str
    
    sar: SARDict
    stop_reason: str
    
    written_to_graph: bool
    graph_case_id: str
    
    tool_calls: int
    tokens: int
    latency_s: float
    step_count: int
