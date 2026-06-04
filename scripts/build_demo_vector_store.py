"""
One-time script to build a SMALLER vector store for demo deployment.
Subsets the dataset to 5000 random cars and embeds them into ChromaDB.
"""

import random
from dotenv import load_dotenv

from app.services.data_loader import load_listings
from app.services.embedding_service import text_from_listing, embed_texts_batch
from app.services.vector_store import VectorStore


load_dotenv()

DEMO_SIZE = 5000
BATCH_SIZE = 100
DEMO_CHROMA_PATH = "data/chroma_db_demo"
DEMO_COLLECTION = "car_listings_demo"


def main():
    print(f"Loading full dataset...")
    all_listings = load_listings("data/raw/dataset.csv")
    
    print(f"Sampling {DEMO_SIZE} cars from {len(all_listings)} total...")
    random.seed(42)  # Reproducibility — same sample each time
    listings = random.sample(all_listings, DEMO_SIZE)
    
    print(f"Initializing demo vector store at {DEMO_CHROMA_PATH}...")
    store = VectorStore(path=DEMO_CHROMA_PATH, collection_name=DEMO_COLLECTION)
    
    already_done = store.count()
    if already_done >= DEMO_SIZE:
        print(f"Demo store already complete ({already_done}/{DEMO_SIZE})")
        return
    
    if already_done > 0:
        print(f"Resuming: {already_done}/{DEMO_SIZE} already embedded")
    
    for batch_start in range(already_done, DEMO_SIZE, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, DEMO_SIZE)
        batch = listings[batch_start:batch_end]
        
        texts = [text_from_listing(listing) for listing in batch]
        embeddings = embed_texts_batch(texts)
        
        store.add(
            ids=[f"demo_{batch_start + i}" for i in range(len(batch))],
            embeddings=embeddings,
            documents=texts,
            metadatas=[listing.to_dict(current_year=2026) for listing in batch],
        )
        
        print(f"Progress: {batch_end}/{DEMO_SIZE}", flush=True)
    
    print(f"\nDone! Demo store has {store.count()} listings.")


if __name__ == "__main__":
    main()