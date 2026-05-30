import random
from fastapi import APIRouter, Request, Query
from datetime import date
from app.models.schemas import CarListingRequest
from app.models.listing import CarListing
from app.services.embedding_service import text_from_listing, embed_text


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


@router.post("/similar")
def find_similar(
    request: Request,
    listing: CarListingRequest,
    n: int = Query(default=5, ge=1, le=20),
) -> list[dict]:
    """
    Find n cars most similar to the input listing.
    """
    # 1. Get vector store from app.state
    vector_store = request.app.state.vector_store

    # 2. Build text from input listing

    input_listing = CarListing(
        make=listing.make,
        model=listing.model,
        year=listing.year,
        km=listing.km,
        price=listing.price
    )
    text = text_from_listing(input_listing)
    # 3. Embed it
    query_embedding = embed_text(text)
    # 4. Query vector store
    results = vector_store.query(query_embedding, top_k=n)
    # 5. Transform response: similarity_score = 1 - distance
    metadatas = results['metadatas'][0]
    distances = results['distances'][0] 

    similar_listings = []

    for metadata, distance in zip(metadatas, distances):
        similarity_score = 1 - distance
        similar_listings.append({**metadata, "similarity_score": similarity_score})

    # 6. Return clean list of dicts
    return similar_listings