import random
from datetime import date

from fastapi import APIRouter, Query, Request

from app.models.listing import CarListing
from app.models.schemas import CarListingRequest
from app.services.llm_service import generate_recommendation
from app.services.pricing_service import analyze_deal
from app.services.similarity_service import find_similar_listings


router = APIRouter(prefix="/listings", tags=["listings"])

@router.post("/analyze")
def analyze_listing(request: Request, payload: CarListingRequest) -> dict:
    listing = CarListing(
        make=payload.make,
        model=payload.model,
        year=payload.year,
        km=payload.km,
        price=payload.price,
    )

    vector_store = request.app.state.vector_store
    similar_listings = find_similar_listings(listing, vector_store, top_k=5)

    current_year = date.today().year
    deal_analysis = analyze_deal(listing, similar_listings, current_year)

    llm_recommendation = generate_recommendation(listing, similar_listings, deal_analysis, current_year)

    return {
        "input": listing.to_dict(current_year),
        "similar_listings": similar_listings,
        **deal_analysis,
        "llm_recommendation": llm_recommendation
    }
    


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


@router.post("/similar")
def find_similar(
    request: Request,
    listing: CarListingRequest,
    n: int = Query(default=5, ge=1, le=20),
) -> list[dict]:
    # Convert Pydantic to domain
    input_listing = CarListing(
        make=listing.make,
        model=listing.model,
        year=listing.year,
        km=listing.km,
        price=listing.price,
    )
    
    # Get vector store
    vector_store = request.app.state.vector_store
    
    # Find similar (delegate to service)
    return find_similar_listings(input_listing, vector_store, top_k=n)