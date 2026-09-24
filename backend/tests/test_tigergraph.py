from app.tools.tigergraph import TigerGraphService

def test_tigergraph_service_initialization():
    tg_service = TigerGraphService()
    # Check that service initializes without throwing exceptions
    assert tg_service is not None
    assert hasattr(tg_service, "get_transaction")
    assert hasattr(tg_service, "get_card")
    assert hasattr(tg_service, "get_customer")
    assert hasattr(tg_service, "get_card_transactions")
    assert hasattr(tg_service, "get_related_transactions")
    assert hasattr(tg_service, "get_device_connections")
    assert hasattr(tg_service, "get_email_connections")
    assert hasattr(tg_service, "get_billing_region")
    assert hasattr(tg_service, "get_closed_cases")
    assert hasattr(tg_service, "get_connected_cards")

def test_get_transaction():
    tg_service = TigerGraphService()
    txn = tg_service.get_transaction("3514030")
    assert txn is not None
    assert "TransactionID" in txn
    assert txn["TransactionID"] == "3514030"

def test_get_card():
    tg_service = TigerGraphService()
    card = tg_service.get_card("C12382-K1")
    assert card is not None
    assert card["card_id"] == "C12382-K1"

def test_get_customer():
    tg_service = TigerGraphService()
    customer = tg_service.get_customer("C12382")
    assert customer is not None
    assert customer["customer_id"] == "C12382"

def test_get_closed_cases():
    tg_service = TigerGraphService()
    cases = tg_service.get_closed_cases(customer_id="C00259")
    assert isinstance(cases, list)
    if cases:
        assert cases[0]["customer_id"] == "C00259"
