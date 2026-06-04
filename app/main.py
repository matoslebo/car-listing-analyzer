import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import listings
from app.services.data_loader import load_listings
from app.services.vector_store import VectorStore

@asynccontextmanager
async def lifespan(app: FastAPI):
    use_demo = os.getenv("USE_DEMO_STORE", "false").lower() == "true"
    
    if use_demo:
        # Demo mode: skip loading listings (dataset.csv not in deployment)
        print("Demo mode: skipping dataset load")
        app.state.listings = []
        
        print("Initializing DEMO vector store...")
        app.state.vector_store = VectorStore(
            path="data/chroma_db_demo",
            collection_name="car_listings_demo",
        )
    else:
        # Full mode: load everything
        print("Loading listings from dataset...")
        app.state.listings = load_listings("data/raw/dataset.csv")
        print(f"Loaded {len(app.state.listings)} listings into memory")
        
        print("Initializing full vector store...")
        app.state.vector_store = VectorStore()
    
    print(f"Vector store ready with {app.state.vector_store.count()} listings")
    
    yield


app = FastAPI(
    title="Car Listing Analyzer",
    version="0.3.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(listings.router)