import pytest
from app.services.vector_store import VectorStore


# Constants for testing
EMBEDDING_DIM = 1536
SAMPLE_METADATA = {
    "make": "BMW",
    "model": "320d",
    "year": 2018,
    "km": 150000,
    "price": 12000,
}


def test_add_increases_count(tmp_path):
    """After adding a listing, count() should return 1."""
    store = VectorStore(
        path=str(tmp_path / "chroma_test"),
        collection_name="test_collection",
    )
    
    assert store.count() == 0
    
    fake_embedding = [0.1] * EMBEDDING_DIM
    store.add(
        ids=["test_1"],
        embeddings=[fake_embedding],
        documents=["BMW 320d, 150000 km"],
        metadatas=[SAMPLE_METADATA],
    )
    
    assert store.count() == 1


def test_query_returns_added_listing(tmp_path):
    """Query with the embedding of an added listing should return that listing."""
    store = VectorStore(
        path=str(tmp_path / "chroma_test"),
        collection_name="test_collection",
    )
    
    fake_embedding = [0.1] * EMBEDDING_DIM
    store.add(
        ids=["bmw_001"],
        embeddings=[fake_embedding],
        documents=["BMW 320d, 150000 km"],
        metadatas=[SAMPLE_METADATA],
    )
    
    results = store.query(fake_embedding, top_k=1)
    
    # Sanity: returned the same id we added
    assert results["ids"][0][0] == "bmw_001"
    assert results["metadatas"][0][0]["make"] == "BMW"


def test_query_identical_embedding_has_zero_distance(tmp_path):
    """Querying with identical embedding should have distance ~0 (cosine metric)."""
    store = VectorStore(
        path=str(tmp_path / "chroma_test"),
        collection_name="test_collection",
    )
    
    fake_embedding = [0.5] * EMBEDDING_DIM
    store.add(
        ids=["test_1"],
        embeddings=[fake_embedding],
        documents=["test"],
        metadatas=[SAMPLE_METADATA],
    )
    
    results = store.query(fake_embedding, top_k=1)
    distance = results["distances"][0][0]
    
    # Cosine distance for identical vectors should be ~0
    # Allow small floating point tolerance
    assert distance < 0.01