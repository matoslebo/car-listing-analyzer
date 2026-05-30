# app/services/embedding_service.py

from openai import OpenAI
from dotenv import load_dotenv
from app.models.listing import CarListing

# Load .env on module import
load_dotenv()

# OpenAI client — uses OPENAI_API_KEY from environment.
# timeout: fail a stalled request after 30s instead of hanging ~10 min on the default.
# max_retries: SDK retries 429/5xx/timeouts with exponential backoff.
client = OpenAI(timeout=30.0, max_retries=5)

EMBEDDING_MODEL = "text-embedding-3-small"


def text_from_listing(listing: CarListing) -> str:
    """
    Convert a CarListing to a text representation for embedding.
    Format: "{year} {make} {model}, {km} km, {price} EUR"
    """
    return f"{listing.year} {listing.make} {listing.model}, {listing.km} km, {listing.price} EUR"


def embed_text(text: str) -> list[float]:
    """
    Generate an embedding for a single text using OpenAI API.
    Returns a list of floats (1536 dimensions for text-embedding-3-small).
    """
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def embed_texts_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple texts in a single API call.
    Returns a list of embeddings (each is a list of floats).
    """
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]