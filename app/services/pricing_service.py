import numpy as np
from app.models.listing import CarListing

# Risk thresholds
OLD_CAR_AGE_THRESHOLD = 15


def calculate_fair_price(similar_listings: list[dict]) -> dict:
    """
    Calculate fair price from a list of similar cars.
    
    Returns:
        {
            "fair_price": int,         # median
            "fair_price_min": int,     # 10th percentile
            "fair_price_max": int,     # 90th percentile
        }
    """

    if not similar_listings:
        raise ValueError("Cannot calculate fair price from empty listings.")
    
    prices = [d['price'] for d in similar_listings]

    fair_price = np.median(prices)
    fair_price_min = np.percentile(prices, 10)
    fair_price_max = np.percentile(prices, 90)

    return {
        "fair_price": int(fair_price),
        "fair_price_min": int(fair_price_min),
        "fair_price_max": int(fair_price_max),
    }
    
def detect_risks(
    listing: CarListing,
    fair_price_range: dict,
    current_year: int,
) -> list[dict]:
    risks = []

    if listing.is_high_mileage(current_year):
        km_per_year = listing.km_per_year(current_year)
        message = f"Mileage is {km_per_year:.0f} km/year, above threshold of 20000"
        risks.append({"type": "high_mileage", "severity": "warning", "message": message})

    if listing.age_in_years(current_year) > OLD_CAR_AGE_THRESHOLD:
        message = f"Car is {listing.age_in_years(current_year)} years old, above threshold of {OLD_CAR_AGE_THRESHOLD} years"
        risks.append({"type": "old_car", "severity": "info", "message": message})
    
    if listing.price > fair_price_range["fair_price_max"]:
        message = f"Price exceeds fair price upper bound ({fair_price_range['fair_price_max']} EUR)"
        risks.append({"type": "above_market_price", "severity": "warning", "message": message})
    
    if listing.price < fair_price_range["fair_price_min"]:
        message = f"Price is below fair price lower bound ({fair_price_range['fair_price_min']} EUR)"
        risks.append({"type": "suspiciously_low_price", "severity": "info", "message": message})
    return risks

def evaluate_deal_quality(
    price: int,
    fair_price: int,
    fair_price_min: int,
    fair_price_max: int,
) -> str:
    """
    Evaluate deal quality based on price position relative to fair price range.
    
    Returns one of: "excellent", "good", "fair", "poor", "overpriced"
    """
    if price < fair_price_min:
        return "excellent"      # below 10th percentile
    elif price < fair_price * 0.92:
        return "good"           # 8% below median
    elif price <= fair_price * 1.08:
        return "fair"           # ±8% around median
    elif price <= fair_price_max:
        return "poor"           # above fair window, but within 90th percentile
    else:
        return "overpriced"     # above 90th percentile
    

def analyze_deal(
    input_listing: CarListing,
    similar_listings: list[dict],
    current_year: int,
) -> dict:
    """
    Orchestrate deal analysis: calculate fair price, detect risks, evaluate quality.
    
    Returns:
        {
            "fair_price": int,
            "fair_price_min": int,
            "fair_price_max": int,
            "deal_quality": str,
            "risks": list[dict],
        }
    """
    # 1. Calculate fair price range
    fair_price_range = calculate_fair_price(similar_listings)

    # 2. Detect risks
    risks = detect_risks(input_listing, fair_price_range, current_year)

    # 3. Evaluate deal quality
    deal_quality = evaluate_deal_quality(
        price=input_listing.price,
        fair_price=fair_price_range["fair_price"],
        fair_price_min=fair_price_range["fair_price_min"],
        fair_price_max=fair_price_range["fair_price_max"],
    )

    # 4. Return combined result
    return {
        **fair_price_range,
        "deal_quality": deal_quality,
        "risks": risks,
    }