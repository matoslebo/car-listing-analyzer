# Car Listing Analyzer

AI-powered tool that analyzes used car listings and recommends whether 
the deal is fair, based on similarity search over a dataset of comparable 
vehicles and an LLM-generated explanation.

> ⚠️ **Status:** Work in progress. Built as a portfolio project to 
> demonstrate AI engineering fundamentals (RAG, FastAPI, Docker, LangChain).

## Overview

Given a used car listing (text input), the system:
1. Extracts structured information (make, model, year, mileage, price)
2. Retrieves similar vehicles from a reference dataset
3. Estimates a fair price range based on comparables
4. Identifies potential risks (e.g. above-average mileage)
5. Generates a natural-language recommendation using an LLM

## Tech Stack

- **FastAPI** — REST API framework
- **Pydantic** — input validation and data modeling
- **ChromaDB** — vector store for similarity search
- **LangChain** — LLM orchestration layer
- **OpenAI API** — recommendation generation
- **Docker** — containerization
- **Streamlit** — minimal frontend (planned)

## Architecture

*Coming soon.*

## Project Structure

​```
app/
  models/      # Domain classes and Pydantic schemas
  services/    # Business logic (pricing, retrieval, LLM)
  api/         # FastAPI route handlers
  main.py      # App entry point
data/          # Reference dataset
notebooks/     # Exploratory data analysis
tests/         # Pytest test suite
​```

## Setup

### Requirements
- Docker & Docker Compose
- Python 3.11+ (for local development without Docker)
- OpenAI API key

### Run with Docker
​```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
docker compose up --build
​```

API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`.

## Usage

*Coming soon.*

## Design Decisions

The project uses two representations:
- `CarListing` — for business logic such as model, year, and km
- `CarListingRequest` — Pydantic model that validates inputs before they reach the handler

This is separated for two reasons:
1. **Separation of concerns** — I can change API structure without change business logic, and vice versa.
2. **Performance** — For example, when I import a lot of records I don't want validate every record because it is problem for performance

### Why FastAPI?

- Type-hint driven design with built-in Pydantic validation
- Auto-generated OpenAPI documentation at `/docs`
- Native async support for future LLM and database calls

### Why Docker?

The Dockerfile uses python:3.11-slim because it is smaller and compatible. Dependencies are copied before application code to leverage Docker layer caching. As a result, pip install is skipped during builds when only the application code changes.

## Roadmap

- [x] Project scaffolding, FastAPI skeleton, Docker setup
- [ ] Dataset ingestion and exploration
- [ ] Vector embeddings + similarity search (ChromaDB)
- [ ] Pricing logic and risk detection
- [ ] LLM-based recommendation (LangChain + OpenAI)
- [ ] Streamlit UI
- [ ] Deployment

## License

MIT