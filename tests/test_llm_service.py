from unittest.mock import patch, MagicMock

from app.models.listing import CarListing
from app.services.llm_service import generate_recommendation


SAMPLE_INPUT = CarListing(
    make="BMW", model="320d", year=2018, km=150000, price=12000
)

SAMPLE_SIMILAR = [
    {"make": "BMW", "model": "320", "year": 2018, "km": 150000, "price": 12000, "similarity_score": 0.95},
]

SAMPLE_DEAL = {
    "fair_price": 14000,
    "fair_price_min": 12000,
    "fair_price_max": 16000,
    "deal_quality": "good",
    "risks": [],
}

FAKE_LLM_OUTPUT = {
    "summary": "Mocked summary for testing.",
    "recommendation": "buy",
    "key_positives": ["Mock positive 1"],
    "key_concerns": [],
}


@patch("app.services.llm_service.chain")
def test_generate_recommendation_returns_validated_output(mock_chain):
    """Test that generate_recommendation returns chain output as-is."""
    mock_chain.invoke.return_value = FAKE_LLM_OUTPUT
    
    result = generate_recommendation(
        input_listing=SAMPLE_INPUT,
        similar_listings=SAMPLE_SIMILAR,
        deal_analysis=SAMPLE_DEAL,
        current_year=2026,
    )
    
    assert result == FAKE_LLM_OUTPUT
    # Sanity: chain.invoke was called exactly once
    mock_chain.invoke.assert_called_once()


@patch("app.services.llm_service.chain")
def test_generate_recommendation_passes_correct_context(mock_chain):
    """Test that chain receives expected context variables."""
    mock_chain.invoke.return_value = FAKE_LLM_OUTPUT
    
    generate_recommendation(
        input_listing=SAMPLE_INPUT,
        similar_listings=SAMPLE_SIMILAR,
        deal_analysis=SAMPLE_DEAL,
        current_year=2026,
    )
    
    # Get the dict that was passed to invoke
    call_args = mock_chain.invoke.call_args
    invoked_with = call_args[0][0]  # first positional argument
    
    # Verify context contains expected keys
    assert "input_car" in invoked_with
    assert "similar_cars" in invoked_with
    assert "pricing_analysis" in invoked_with
    assert "risks" in invoked_with
    assert "format_instructions" in invoked_with
    
    # Verify input car text contains the listing details
    assert "BMW" in invoked_with["input_car"]
    assert "320d" in invoked_with["input_car"]
    assert "12000" in invoked_with["input_car"]