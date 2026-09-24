from typing import List, Literal
from pydantic import BaseModel, Field

ApprovalRoute = Literal["auto", "L1", "L2"]

class ActionRecommendation(BaseModel):
    action: str = Field(..., description="Action identifier from Fraud Policy Section 1")
    route: ApprovalRoute = Field(..., description="Approval route: auto, L1, or L2")
    reason: str = Field(..., description="Policy rule citation and justification")

class NextBestActions(BaseModel):
    initial: List[ActionRecommendation] = Field(..., description="Actions recommended before requested evidence came back")
    final: List[ActionRecommendation] = Field(..., description="Actions recommended after evidence/assumptions")
    what_changed: str = Field(..., description="Explanation of why final differs from initial, or 'nothing'")
