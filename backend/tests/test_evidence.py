from app.models.evidence import EvidenceItem
from app.services.evidence_service import evidence_service
from app.services.case_service import case_service

def test_evidence_item_structure():
    ev = EvidenceItem(
        claim="Transaction 3514030 flagged with risk score 0.61",
        source="graph",
        ref="query:get_transaction(txn_id=3514030)",
        entity_ids=["3514030", "C12382-K1"]
    )
    assert ev.claim.startswith("Transaction 3514030")
    assert ev.source == "graph"
    assert ev.ref == "query:get_transaction(txn_id=3514030)"
    assert "3514030" in ev.entity_ids

def test_extract_evidence_for_case():
    case_item = case_service.get_case_by_id("HHG-001")
    assert case_item is not None

    evidence = evidence_service.extract_evidence_for_case(case_item)
    assert isinstance(evidence, list)
    assert len(evidence) > 0

    for ev in evidence:
        assert isinstance(ev, EvidenceItem)
        assert ev.claim != ""
        assert ev.source in ["graph", "document", "customer", "external"]
        assert ev.ref != ""
        assert isinstance(ev.entity_ids, list)
