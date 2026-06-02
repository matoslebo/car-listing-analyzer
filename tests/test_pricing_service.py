import pytest

from app.models.listing import CarListing
from app.services.pricing_service import (
    calculate_fair_price,
    detect_risks,
    evaluate_deal_quality,
    analyze_deal,
)


# Fixtures — sample data reused across tests
SAMPLE_LISTINGS = [
    {"make": "BMW", "model": "320", "year": 2018, "km": 150000, "price": 10000},
    {"make": "BMW", "model": "320", "year": 2019, "km": 140000, "price": 12000},
    {"make": "BMW", "model": "320", "year": 2018, "km": 160000, "price": 14000},
    {"make": "BMW", "model": "320", "year": 2017, "km": 170000, "price": 16000},
    {"make": "BMW", "model": "320", "year": 2020, "km": 130000, "price": 18000},
]

def test_calculate_fair_price_returns_median_and_percentiles():
    result = calculate_fair_price(SAMPLE_LISTINGS)
    
    # Median of [10000, 12000, 14000, 16000, 18000] = 14000
    assert result["fair_price"] == 14000
    # 10th percentile and 90th percentile
    assert "fair_price_min" in result
    assert "fair_price_max" in result
    assert result["fair_price_min"] < result["fair_price"] < result["fair_price_max"]

def test_calculate_fair_price_raises_on_empty():
    with pytest.raises(ValueError, match="empty listings"):
        calculate_fair_price([])


def test_detect_risks_high_mileage_creates_warning():
    # Car with 30k km/year (high mileage)
    listing = CarListing(
        make="BMW", model="320d", year=2020, km=180000, price=15000
    )
    fair_price_range = {"fair_price": 15000, "fair_price_min": 12000, "fair_price_max": 18000}
    
    risks = detect_risks(listing, fair_price_range, current_year=2026)
    
    # Find the high_mileage risk
    high_mileage_risks = [r for r in risks if r["type"] == "high_mileage"]
    assert len(high_mileage_risks) == 1
    assert high_mileage_risks[0]["severity"] == "warning"

def test_detect_risks_no_risks_returns_empty_list():
    # Modern car, low mileage, price in fair range
    listing = CarListing(
        make="BMW", model="320d", year=2024, km=20000, price=15000
    )
    fair_price_range = {"fair_price": 15000, "fair_price_min": 12000, "fair_price_max": 18000}
    
    risks = detect_risks(listing, fair_price_range, current_year=2026)
    
    assert risks == []

@pytest.mark.parametrize("price,expected", [
    (5000, "excellent"),    # below fair_price_min (10000)
    (11000, "good"),        # below fair_price * 0.92 (13800)
    (15000, "fair"),        # around median (15000)
    (17000, "poor"),        # above fair_price * 1.08 (16200), within max (18000)
    (25000, "overpriced"),  # above fair_price_max (18000)
])
def test_evaluate_deal_quality_all_categories(price, expected):
    result = evaluate_deal_quality(
        price=price,
        fair_price=15000,
        fair_price_min=10000,
        fair_price_max=18000,
    )
    assert result == expected

def test_analyze_deal_integration():
    listing = CarListing(
        make="BMW", model="320d", year=2018, km=150000, price=14000
    )
    
    result = analyze_deal(listing, SAMPLE_LISTINGS, current_year=2026)
    
    # Check all keys present
    assert "fair_price" in result
    assert "fair_price_min" in result
    assert "fair_price_max" in result
    assert "deal_quality" in result
    assert "risks" in result
    
    # Sanity: 14000 == median, should be "fair"
    assert result["deal_quality"] == "fair"