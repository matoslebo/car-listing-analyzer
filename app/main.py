from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import listings
from app.services.data_loader import load_listings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load dataset into memory once
    print("Loading listings from dataset...")
    app.state.listings = load_listings("data/raw/dataset.csv")
    print(f"Loaded {len(app.state.listings)} listings into memory")
    
    yield  # App runs here
    
    # Shutdown: cleanup (nothing to clean up yet)


app = FastAPI(
    title="Car Listing Analyzer",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(listings.router)