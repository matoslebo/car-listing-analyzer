import random
from fastapi import APIRouter, Request, Query
from datetime import date
from app.models.schemas import CarListingRequest
from app.models.listing import CarListing


router = APIRouter(prefix="/listings", tags=["listings"])

@router.post("/analyze")
def analyze_listing(request: CarListingRequest) -> dict:
    listing = CarListing(
        make=request.make,
        model=request.model,
        year=request.year,
        km=request.km,
        price=request.price
    )

    current_year = date.today().year
    result = listing.to_dict(current_year)

    return result


@router.get("/sample")
def get_sample(
    request: Request,
    n: int = Query(default=5, ge=1, le=100, description="Number of samples")
) -> list[dict]:
    # Access listings loaded at app startup via app.state
    listings = request.app.state.listings
    
    # Random sample without replacement
    sample = random.sample(listings, min(n, len(listings)))
    
    current_year = date.today().year 
    return [listing.to_dict(current_year) for listing in sample]