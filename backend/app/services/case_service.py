import csv
import os
from typing import List, Optional
from app.config import settings
from app.models.case import CasePackItem
from app.utils.logging import logger

class CaseService:
    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = csv_path or settings.CASE_PACK_PATH
        self._cases_cache: Optional[List[CasePackItem]] = None

    def _load_cases(self) -> List[CasePackItem]:
        if self._cases_cache is not None:
            return self._cases_cache

        if not os.path.exists(self.csv_path):
            logger.error(f"case_pack.csv not found at path: {self.csv_path}")
            return []

        cases = []
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                risk_score_val = None
                raw_score = row.get("risk_score", "").strip()
                if raw_score:
                    try:
                        risk_score_val = float(raw_score)
                    except ValueError:
                        risk_score_val = None

                case_item = CasePackItem(
                    case_id=row["case_id"].strip(),
                    opened_at=row["opened_at"].strip(),
                    trigger_type=row["trigger_type"].strip(),
                    trigger_text=row["trigger_text"].strip(),
                    flagged_txn_id=row["flagged_txn_id"].strip(),
                    card_id=row["card_id"].strip(),
                    customer_id=row["customer_id"].strip(),
                    risk_score=risk_score_val
                )
                cases.append(case_item)

        self._cases_cache = cases
        logger.info(f"Loaded {len(cases)} benchmark cases from {self.csv_path}")
        return cases

    def get_all_cases(self) -> List[CasePackItem]:
        return self._load_cases()

    def get_case_by_id(self, case_id: str) -> Optional[CasePackItem]:
        cases = self._load_cases()
        for c in cases:
            if c.case_id == case_id:
                return c
        return None

case_service = CaseService()
