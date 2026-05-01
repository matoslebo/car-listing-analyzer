from fastapi import FastAPI
from app.api import listings


app = FastAPI(title="Car Listing Analyzer", version="0.1.0")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(listings.router)


