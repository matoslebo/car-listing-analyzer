from fastapi import APIRouter
from datetime import date
from app.models.schemas import CarListingRequest
from app.models.listing import CarListing


router = APIRouter(prefix="/listings", tags=["listings"])

@router.post("/analyze")
def analyze_listing(request: CarListingRequest) -> dict:
    # 1. Z Pydantic schémy vytvor domain model CarListing
    listing = CarListing(
        make=request.make,
        model=request.model,
        year=request.year,
        km=request.km,
        price=request.price
    )
    # 2. Zavolaj to_dict() s aktuálnym rokom
    current_year = date.today().year
    result = listing.to_dict(current_year)
    # 3. Vráť výsledok
    return result