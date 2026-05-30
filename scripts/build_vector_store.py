"""
One-time script to embed all car listings and store them in ChromaDB.

Usage:
    python -m scripts.build_vector_store
"""

from app.services.data_loader import load_listings
from app.services.embedding_service import text_from_listing, embed_texts_batch
from app.services.vector_store import VectorStore

BATCH_SIZE = 100
DATASET_PATH = "data/raw/dataset.csv"


def build_vector_store():
    # Step 1: Initialize VectorStore
    store = VectorStore()

    # Step 2: Load and clean listings
    listings = load_listings(DATASET_PATH)
    total = len(listings)

    # Step 3: Resume from where a previous run left off.
    # Each batch is persisted atomically, so count() is the number of listings
    # already embedded — and the index of the next one to process.
    already_done = store.count()
    if already_done >= total:
        print(f"Collection already complete with {already_done} listings. Nothing to do.")
        print("To rebuild from scratch: delete data/chroma_db/ and rerun.")
        return
    if already_done > 0:
        print(f"Resuming: {already_done}/{total} already embedded.")
    print(f"Embedding {total} listings in batches of {BATCH_SIZE}...")

    # Step 4: Process in batches, starting after what's already stored
    for batch_start in range(already_done, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch = listings[batch_start:batch_end]
        
        # Prepare batch data
        ids = [f"listing_{i}" for i in range(batch_start, batch_end)]
        texts = [text_from_listing(l) for l in batch]
        metadatas = [
            {
                "make": l.make,
                "model": l.model,
                "year": l.year,
                "km": l.km,
                "price": l.price,
            }
            for l in batch
        ]
        
        # Embed batch (1 API call for 100 texts)
        embeddings = embed_texts_batch(texts)
        
        # Add to vector store
        store.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        
        # Progress log every 1000 (flush so a stalled run is visibly stalled, not buffered)
        if batch_end % 1000 == 0 or batch_end == total:
            print(f"Progress: {batch_end}/{total} ({100*batch_end//total}%)", flush=True)

    print(f"Done. Vector store now contains {store.count()} listings.")


if __name__ == "__main__":
    build_vector_store()