import os
import csv
from typing import List, Dict, Any, Optional
from app.utils.logging import logger

class CaseMemory:
    def __init__(self, history_csv_path: Optional[str] = None):
        if history_csv_path:
            self.history_csv_path = history_csv_path
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            # Check backend/data/closed_cases_history.csv, then root closed_cases_history.csv
            opt1 = os.path.join(base_dir, "data", "closed_cases_history.csv")
            opt2 = os.path.join(os.path.dirname(base_dir), "closed_cases_history.csv")
            opt3 = os.path.join(base_dir, "closed_cases_history.csv")
            
            if os.path.exists(opt1):
                self.history_csv_path = opt1
            elif os.path.exists(opt2):
                self.history_csv_path = opt2
            else:
                self.history_csv_path = opt3

        self._history_cache: Optional[List[Dict[str, Any]]] = None

    def _load_history(self) -> List[Dict[str, Any]]:
        if self._history_cache is not None:
            return self._history_cache

        if not os.path.exists(self.history_csv_path):
            logger.warning(f"closed_cases_history.csv not found at {self.history_csv_path}")
            return []

        history = []
        with open(self.history_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                history.append(row)

        self._history_cache = history
        logger.info(f"Loaded {len(history)} closed historical cases into CaseMemory from {self.history_csv_path}")
        return history

    def search_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Find past investigations for the same customer."""
        all_cases = self._load_history()
        return [c for c in all_cases if c.get("customer_id") == customer_id]

    def search_by_card(self, card_id: str) -> List[Dict[str, Any]]:
        """Find past investigations on the exact same card."""
        all_cases = self._load_history()
        return [c for c in all_cases if c.get("card_id") == card_id]

    def search_by_connected_cards(self, connected_card_ids: List[str]) -> List[Dict[str, Any]]:
        """Find past investigations involving connected cards."""
        all_cases = self._load_history()
        matches = []
        target_set = set(connected_card_ids)
        for c in all_cases:
            if c.get("card_id") in target_set:
                matches.append(c)
                continue
            hist_connected = c.get("connected_card_ids", "").split("|")
            if any(cc in target_set for cc in hist_connected if cc):
                matches.append(c)
        return matches

    def search_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Find past investigations with matching fraud patterns."""
        all_cases = self._load_history()
        return [c for c in all_cases if c.get("pattern") == pattern]

    def retrieve_similar_prior_cases(
        self,
        customer_id: Optional[str] = None,
        card_id: Optional[str] = None,
        connected_cards: Optional[List[str]] = None,
        pattern: Optional[str] = None
    ) -> List[str]:
        """
        Retrieve relevant historical closed_case IDs.
        Returns list of case_ids (e.g. ['CC-0141', 'CC-2671']).
        """
        similar_ids: List[str] = []
        all_cases = self._load_history()

        # Priority 1: Exact card match
        if card_id:
            for c in all_cases:
                if c.get("card_id") == card_id:
                    cid = c.get("case_id")
                    if cid and cid not in similar_ids:
                        similar_ids.append(cid)

        # Priority 2: Same customer match
        if customer_id:
            for c in all_cases:
                if c.get("customer_id") == customer_id:
                    cid = c.get("case_id")
                    if cid and cid not in similar_ids:
                        similar_ids.append(cid)

        # Priority 3: Connected card match
        if connected_cards:
            for c in self.search_by_connected_cards(connected_cards):
                cid = c.get("case_id")
                if cid and cid not in similar_ids:
                    similar_ids.append(cid)

        # Priority 4: Pattern match if few results found
        if pattern and len(similar_ids) < 3:
            for c in all_cases:
                if c.get("pattern") == pattern:
                    cid = c.get("case_id")
                    if cid and cid not in similar_ids:
                        similar_ids.append(cid)
                    if len(similar_ids) >= 5:
                        break

        return similar_ids[:5]

case_memory = CaseMemory()
