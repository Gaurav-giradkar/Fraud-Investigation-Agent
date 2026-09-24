from typing import List, Dict, Any, Optional
from app.models.evidence import EvidenceItem
from app.models.case import CasePackItem
from app.tools.tigergraph import TigerGraphService
from app.utils.logging import logger

class EvidenceService:
    def __init__(self, tg_service: Optional[TigerGraphService] = None):
        from app.tools.tigergraph import tigergraph_service
        self.tg_service = tg_service or tigergraph_service

    def build_transaction_evidence(self, txn: Dict[str, Any], card_id: str) -> EvidenceItem:
        txn_id = str(txn.get("TransactionID", ""))
        amt = txn.get("TransactionAmt", 0.0)
        ts = txn.get("ts", "")
        risk_score = txn.get("risk_score", 0.0)
        channel = txn.get("channel", "online")
        addr1 = txn.get("addr1", "")
        
        claim = f"Transaction {txn_id} on card {card_id} for ${amt:.2f} at {ts} (channel: {channel}"
        if addr1:
            claim += f", billing region: {addr1}"
        if risk_score is not None:
            claim += f", risk_score: {risk_score:.2f}"
        claim += ")."

        return EvidenceItem(
            claim=claim,
            source="graph",
            ref=f"query:get_transaction(txn_id={txn_id})",
            entity_ids=[txn_id, card_id]
        )

    def build_card_history_evidence(self, card_id: str, txns: List[Dict[str, Any]]) -> EvidenceItem:
        txn_ids = [str(t.get("TransactionID", "")) for t in txns if t.get("TransactionID")]
        count = len(txns)
        total_amt = sum(float(t.get("TransactionAmt", 0)) for t in txns)
        claim = f"Card {card_id} has {count} recorded transaction(s) totaling ${total_amt:.2f}."
        
        return EvidenceItem(
            claim=claim,
            source="graph",
            ref=f"query:get_card_transactions(card_id={card_id})",
            entity_ids=[card_id] + txn_ids
        )

    def build_device_link_evidence(self, device_profile: str, entity_ids: List[str]) -> EvidenceItem:
        claim = f"Device profile '{device_profile}' is associated with entities: {', '.join(entity_ids)}."
        return EvidenceItem(
            claim=claim,
            source="graph",
            ref="query:get_device_connections",
            entity_ids=entity_ids
        )

    def build_closed_case_evidence(self, prior_case: Dict[str, Any]) -> EvidenceItem:
        case_id = prior_case.get("case_id", "")
        outcome = prior_case.get("outcome", "")
        pattern = prior_case.get("pattern", "")
        notes = prior_case.get("analyst_notes", "")
        card_id = prior_case.get("card_id", "")

        claim = f"Historical case {case_id} (outcome: {outcome}, pattern: {pattern}) on card {card_id}: {notes[:150]}..."
        entity_ids = [case_id]
        if card_id:
            entity_ids.append(card_id)

        return EvidenceItem(
            claim=claim,
            source="graph",
            ref=f"query:get_closed_cases(case_id={case_id})",
            entity_ids=entity_ids
        )

    def build_customer_response_evidence(
        self, request_id: str, claim: str, entity_ids: Optional[List[str]] = None
    ) -> EvidenceItem:
        return EvidenceItem(
            claim=claim,
            source="customer",
            ref=f"evidence_request:{request_id}",
            entity_ids=entity_ids or []
        )

    def extract_evidence_for_case(self, case_item: CasePackItem) -> List[EvidenceItem]:
        evidence_list: List[EvidenceItem] = []
        
        # 1. Flagged transaction evidence
        txn = self.tg_service.get_transaction(case_item.flagged_txn_id)
        if txn:
            evidence_list.append(self.build_transaction_evidence(txn, case_item.card_id))

        # 2. Card transactions evidence
        card_txns = self.tg_service.get_card_transactions(case_item.card_id)
        if card_txns:
            evidence_list.append(self.build_card_history_evidence(case_item.card_id, card_txns))

        # 3. Prior closed cases evidence
        closed_cases = self.tg_service.get_closed_cases(
            customer_id=case_item.customer_id, card_id=case_item.card_id
        )
        for cc in closed_cases[:2]:
            evidence_list.append(self.build_closed_case_evidence(cc))

        return evidence_list

evidence_service = EvidenceService()
