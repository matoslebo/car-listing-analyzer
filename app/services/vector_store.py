import chromadb

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "car_listings_v1"


class VectorStore:
    """
    Wrapper around ChromaDB for car listings similarity search.
    """
    
    def __init__(self, path: str = CHROMA_PATH, collection_name: str = COLLECTION_NAME):
        # Persistent client — survives app restarts
        self.client = chromadb.PersistentClient(path=path)
        # get_or_create_collection: create if missing, return existing if exists
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    
    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """
        Add embeddings to the collection.
        
        ids: unique identifier per listing (e.g. "listing_0", "listing_1")
        embeddings: list of 1536-dim vectors
        documents: original text that was embedded (for retrieval display)
        metadatas: structured data per listing (make, model, year, km, price)
        """
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
    
    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> dict:
        """
        Find the top_k most similar listings to the query embedding.
        Returns ChromaDB's native response format.
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
    
    def count(self) -> int:
        """Return number of listings in the collection."""
        return self.collection.count()