import os
import csv
from typing import Dict, Any, List, Optional
from app.config import settings
from app.utils.logging import logger

try:
    import pyTigerGraph as tg
except ImportError:
    tg = None

class TigerGraphService:
    def __init__(
        self,
        host: Optional[str] = None,
        graph: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        secret: Optional[str] = None
    ):
        self.host = host or settings.TIGERGRAPH_HOST
        self.graph = graph or settings.TIGERGRAPH_GRAPH
        self.username = username or settings.TIGERGRAPH_USERNAME
        self.password = password or settings.TIGERGRAPH_PASSWORD
        self.secret = secret or settings.TIGERGRAPH_SECRET
        
        self.conn = None
        self._connected = False
        self._init_connection()

    def _init_connection(self):
        if not tg:
            logger.warning("pyTigerGraph package not installed; running in mock/fallback mode.")
            return

        try:
            # Initialize connection using credentials
            self.conn = tg.TigerGraphConnection(
                host=self.host,
                graphname=self.graph,
                username=self.username,
                password=self.password
            )
            if self.secret:
                self.conn.secret = self.secret
                self.conn.getToken(self.secret)
            self._connected = True
            logger.info(f"Initialized TigerGraph connection to {self.host} graph={self.graph}")
        except Exception as e:
            logger.warning(f"Could not connect to live TigerGraph instance at {self.host}: {e}. Fallback mode active.")
            self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def get_transaction(self, txn_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction details by TransactionID."""
        if self._connected and self.conn:
            try:
                res = self.conn.getVerticesById("Transaction", txn_id)
                if res:
                    return res[0] if isinstance(res, list) else res
            except Exception as e:
                logger.error(f"TG Error in get_transaction({txn_id}): {e}")
        
        # Fallback / local schema return
        return {
            "TransactionID": str(txn_id),
            "customer_id": "C12382",
            "card_id": "C12382-K1",
            "TransactionAmt": 77.07,
            "ts": "2016-12-05 01:55:28",
            "channel": "in_person",
            "risk_score": 0.61,
            "addr1": 444.0,
            "addr2": 87.0
        }

    def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get card details by card_id."""
        if self._connected and self.conn:
            try:
                res = self.conn.getVerticesById("Card", card_id)
                if res:
                    return res[0] if isinstance(res, list) else res
            except Exception as e:
                logger.error(f"TG Error in get_card({card_id}): {e}")
                
        return {
            "card_id": card_id,
            "customer_id": card_id.split("-")[0] if "-" in card_id else card_id,
            "card4": "visa",
            "card6": "credit"
        }

    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer details by customer_id."""
        if self._connected and self.conn:
            try:
                res = self.conn.getVerticesById("Customer", customer_id)
                if res:
                    return res[0] if isinstance(res, list) else res
            except Exception as e:
                logger.error(f"TG Error in get_customer({customer_id}): {e}")

        return {
            "customer_id": customer_id,
            "cards": [f"{customer_id}-K1", f"{customer_id}-K2"]
        }

    def get_card_transactions(self, card_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all transactions associated with a card."""
        if self._connected and self.conn:
            try:
                edges = self.conn.getEdges("Card", card_id, "MADE", limit=limit)
                return edges
            except Exception as e:
                logger.error(f"TG Error in get_card_transactions({card_id}): {e}")

        return [
            {
                "TransactionID": "3514030",
                "card_id": card_id,
                "TransactionAmt": 77.07,
                "ts": "2016-12-05 01:55:28",
                "risk_score": 0.61,
                "addr1": 444.0
            }
        ]

    def get_related_transactions(self, card_id: str) -> List[Dict[str, Any]]:
        """Get related transactions for a card."""
        return self.get_card_transactions(card_id, limit=50)

    def get_device_connections(self, device_profile_id: str) -> List[Dict[str, Any]]:
        """Get transactions or cards sharing a specific device profile."""
        if self._connected and self.conn:
            try:
                edges = self.conn.getEdges("DeviceProfile", device_profile_id, "FROM_DEVICE")
                return edges
            except Exception as e:
                logger.error(f"TG Error in get_device_connections({device_profile_id}): {e}")

        return []

    def get_email_connections(self, email_domain: str) -> List[Dict[str, Any]]:
        """Get transactions sharing an email domain."""
        if self._connected and self.conn:
            try:
                edges = self.conn.getEdges("EmailDomain", email_domain, "PURCHASER_EMAIL")
                return edges
            except Exception as e:
                logger.error(f"TG Error in get_email_connections({email_domain}): {e}")

        return []

    def get_billing_region(self, region_id: str) -> List[Dict[str, Any]]:
        """Get transactions billed in a specific region."""
        if self._connected and self.conn:
            try:
                edges = self.conn.getEdges("BillingRegion", region_id, "BILLED_IN")
                return edges
            except Exception as e:
                logger.error(f"TG Error in get_billing_region({region_id}): {e}")

        return []

    def get_closed_cases(self, customer_id: Optional[str] = None, card_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get historical closed cases filtered by customer_id or card_id."""
        if self._connected and self.conn:
            try:
                if card_id:
                    edges = self.conn.getEdges("Card", card_id, "ON_CARD")
                    if edges:
                        return edges
            except Exception as e:
                logger.error(f"TG Error in get_closed_cases({customer_id}, {card_id}): {e}")

        # Local fallback reading closed_cases_history.csv if available
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "closed_cases_history.csv"
        )
        results = []
        if os.path.exists(csv_path):
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    match_cust = (customer_id is None or row.get("customer_id") == customer_id)
                    match_card = (card_id is None or row.get("card_id") == card_id)
                    if match_cust and match_card:
                        results.append(row)
                        if len(results) >= 20:
                            break
        return results

    def get_connected_cards(self, device_id: str) -> List[Dict[str, Any]]:
        """Get cards connected through a shared device profile."""
        if self._connected and self.conn:
            try:
                edges = self.conn.getEdges("DeviceProfile", device_id, "CONNECTED_TO")
                return edges
            except Exception as e:
                logger.error(f"TG Error in get_connected_cards({device_id}): {e}")

        return []

tigergraph_service = TigerGraphService()
