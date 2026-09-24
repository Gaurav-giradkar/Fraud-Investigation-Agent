from app.tools.case_memory import case_memory

def test_search_by_customer():
    cases = case_memory.search_by_customer("C00259")
    assert isinstance(cases, list)
    assert len(cases) > 0
    assert cases[0]["customer_id"] == "C00259"
    assert cases[0]["case_id"] == "CC-0001"

def test_search_by_card():
    cases = case_memory.search_by_card("C06403-K2")
    assert isinstance(cases, list)
    assert len(cases) > 0
    assert cases[0]["card_id"] == "C06403-K2"
    assert cases[0]["case_id"] == "CC-0002"

def test_retrieve_similar_prior_cases():
    similar_ids = case_memory.retrieve_similar_prior_cases(
        customer_id="C00259", card_id="C00259-K1", pattern="card_not_present_fraud"
    )
    assert isinstance(similar_ids, list)
    assert "CC-0001" in similar_ids
