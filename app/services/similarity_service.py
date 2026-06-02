# app/services/similarity_service.py

from app.models.listing import CarListing
from app.services.embedding_service import text_from_listing, embed_text
from app.services.vector_store import VectorStore


def find_similar_listings(
    input_listing: CarListing,
    vector_store: VectorStore,
    top_k: int = 5,
) -> list[dict]:
    """
    Find top_k cars most similar to the input listing.
    
    Returns list of dicts with metadata + similarity_score.
    """
    # 1. Build text representation
    text = text_from_listing(input_listing)
    
    # 2. Embed it
    query_embedding = embed_text(text)
    
    # 3. Query vector store
    results = vector_store.query(query_embedding, top_k=top_k)
    
    # 4. Transform raw ChromaDB response
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    similar_listings = []
    for metadata, distance in zip(metadatas, distances):
        similarity_score = 1 - distance
        similar_listings.append({**metadata, "similarity_score": similarity_score})
    
    return similar_listings