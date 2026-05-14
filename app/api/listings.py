from fastapi import APIRouter
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