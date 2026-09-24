from typing import Optional, List
from pydantic import BaseModel, Field

class CasePackItem(BaseModel):
    case_id: str = Field(..., description="Unique case ID, e.g. HHG-001")
    opened_at: str = Field(..., description="Case opening timestamp")
    trigger_type: str = Field(..., description="risk_score | customer_report | analyst_request")
    trigger_text: str = Field(..., description="Description of the alert trigger")
    flagged_txn_id: str = Field(..., description="ID of the flagged transaction")
    card_id: str = Field(..., description="ID of the card under investigation")
    customer_id: str = Field(..., description="ID of the customer who owns the card")
    risk_score: Optional[float] = Field(None, description="Risk score if trigger_type is risk_score")
