from app.services.evidence_service import evidence_service, EvidenceItem
from app.models.case import CasePackItem
from typing import List

def gather_evidence_for_case(case_item: CasePackItem) -> List[EvidenceItem]:
    """Helper tool to gather structured evidence for a benchmark case."""
    return evidence_service.extract_evidence_for_case(case_item)
