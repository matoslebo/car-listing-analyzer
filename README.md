# 🚗 Car Listing Analyzer

AI-powered tool to analyze used car listings — extracts key details, finds similar vehicles from the market, estimates fair pricing, detects risks, and provides natural-language recommendations.

**Live demo:** https://car-listing-analyzer-hzkelau5hqo6t5whgjy9qk.streamlit.app
**API docs:** https://car-listing-analyzer.onrender.com/docs

## What it does

Input a car listing (make, model, year, mileage, price) and get:
- **Fair price estimate** with 10th-90th percentile range from similar market listings
- **Deal quality** rating: excellent / good / fair / poor / overpriced
- **Risk detection**: high mileage, old car, suspicious pricing, above market
- **AI recommendation**: buy / inspect_then_buy / negotiate / avoid with natural language summary

## Architecture
User → Streamlit UI → FastAPI backend → ChromaDB (vector search)
→ Pricing engine (statistical analysis)
→ LangChain + OpenAI GPT-4o-mini (LLM advisor)

## Tech stack

- **Backend:** FastAPI, Pydantic, Python 3.11
- **Vector search:** ChromaDB with OpenAI text-embedding-3-small (1536-dim, cosine similarity)
- **LLM orchestration:** LangChain (LCEL chains, structured output via JsonOutputParser)
- **Pricing logic:** numpy (median, percentiles), custom risk detection
- **Frontend:** Streamlit with reactive form
- **Infrastructure:** Docker Compose, deployed on Render (backend) + Streamlit Cloud (frontend)
- **Testing:** pytest with mocked LLM tests (18 tests across data, vector store, pricing, LLM)
- **Data:** Kaggle "EU Used Cars" dataset (40k listings, cleaned to 37k)

## Design decisions

- **Median + percentiles, not mean** — robust to outliers in skewed price distributions
- **Cosine similarity (not L2 default)** — better for semantic embedding comparison
- **gpt-4o-mini, temperature 0.3** — consistent business recommendations with mild variation
- **Pydantic schema for LLM output** — Literal enum forces valid recommendation values; JsonOutputParser validates structure
- **Separate similarity service** — DRY pattern, used by both `/similar` and `/analyze` endpoints
- **Demo mode (5000 cars) for deployment** — fits Render free tier; full dataset (37k) for local development
- **Multi-service Docker** — frontend and backend as separate containers, communicate via service name

## Local setup

```bash
# 1. Clone
git clone https://github.com/matoslebo/car-listing-analyzer
cd car-listing-analyzer

# 2. Download dataset from Kaggle
# https://www.kaggle.com/datasets/alemazz11/eu-used-cars
# Place CSV at data/raw/dataset.csv

# 3. Configure environment
cp .env.example .env
# Add OPENAI_API_KEY to .env

# 4. Build full vector store (one-time, ~3 minutes, ~$0.01)
python -m scripts.build_vector_store

# 5. Run with Docker Compose
docker compose up --build

# 6. Open
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:8501
```

## Project structure
car-listing-analyzer/
├── app/
│   ├── api/listings.py             # FastAPI endpoints
│   ├── models/                     # Domain class + Pydantic schemas
│   ├── services/
│   │   ├── data_loader.py          # CSV → CarListing pipeline
│   │   ├── embedding_service.py    # OpenAI embeddings
│   │   ├── vector_store.py         # ChromaDB wrapper
│   │   ├── similarity_service.py   # find_similar_listings()
│   │   ├── pricing_service.py      # fair price, risks, deal quality
│   │   └── llm_service.py          # LangChain + structured output
│   └── main.py                     # FastAPI app + lifespan
├── frontend/
│   ├── streamlit_app.py            # Streamlit UI
│   └── Dockerfile
├── scripts/
│   ├── build_vector_store.py       # Full dataset embedding pipeline
│   └── build_demo_vector_store.py  # 5k sample for deployment
├── tests/                          # 18 pytest tests
├── notebooks/                      # Data exploration
└── notes.md                        # Engineering journal across 6 weekends

## Test suite

```bash
pytest tests/ -v
```

Coverage:
- Data loading + cleaning (5 tests)
- Vector store operations (3 tests)
- Pricing logic + risks + deal quality (10 tests, including parametrized)
- LLM service with mocked chain (2 tests)

## License

MIT — see LICENSE file