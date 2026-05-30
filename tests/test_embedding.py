from app.services.data_loader import load_listings
from app.services.embedding_service import text_from_listing, embed_text, embed_texts_batch

# Load couple of listings
listings = load_listings("data/raw/dataset.csv")
print(f"Loaded {len(listings)} listings")

# Test text representation
test_listing = listings[0]
text = text_from_listing(test_listing)
print(f"Text: {text}")

# Test single embedding
embedding = embed_text(text)
print(f"Embedding dimensions: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")

# Test batch embedding
batch_texts = [text_from_listing(l) for l in listings[:3]]
batch_embeddings = embed_texts_batch(batch_texts)
print(f"Batch returned {len(batch_embeddings)} embeddings")
print(f"Each dimension: {len(batch_embeddings[0])}")