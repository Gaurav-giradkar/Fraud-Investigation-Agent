from typing import List, Literal
from pydantic import BaseModel, Field

EvidenceSource = Literal["graph", "document", "customer", "external"]

class EvidenceItem(BaseModel):
    claim: str = Field(..., description="Concise, factual statement of evidence found")
    source: EvidenceSource = Field(..., description="Origin of the evidence: graph, document, customer, or external")
    ref: str = Field(..., description="Reference query name, document section, or evidence request ID")
    entity_ids: List[str] = Field(default_factory=list, description="List of dataset IDs (txns, cards, customers, devices, etc.) the claim rests on")
