from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_all_cases():
    response = client.get("/api/cases")
    assert response.status_code == 200
    cases = response.json()
    assert isinstance(cases, list)
    assert len(cases) == 20

def test_get_case_hhg_001():
    response = client.get("/api/cases/HHG-001")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "HHG-001"
    assert data["opened_at"] == "2016-12-05 01:55:28"
    assert data["trigger_type"] == "risk_score"
    assert "Real-time model scored transaction 3514030" in data["trigger_text"]
    assert data["flagged_txn_id"] == "3514030"
    assert data["card_id"] == "C12382-K1"
    assert data["customer_id"] == "C12382"
    assert data["risk_score"] == 0.61

def test_get_case_not_found():
    response = client.get("/api/cases/HHG-999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
