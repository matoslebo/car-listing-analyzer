from typing import Literal 
from pydantic import BaseModel, Field

class CarListingRequest(BaseModel):

    make: str = Field(..., min_length=2, max_length=30, description="The make of the car")
    model: str = Field(..., min_length=2, max_length=30, description="The model of the car")
    year: int = Field(..., ge=1900, le=2026, description="The year the car was manufactured")
    km: int = Field(..., ge=0, description="The number of kilometers the car has been driven")
    price: int = Field(..., ge=0, le=1000000, description="The price of the car")


class LLMRecommendation(BaseModel):
    """Schema for LLM-generated deal recommendation."""
    
    summary: str = Field(
        ...,
        description="Natural language summary of the deal (2-3 sentences)",
    )
    recommendation: Literal["buy", "inspect_then_buy", "negotiate", "avoid"] = Field(
        ...,
        description="Final recommendation for the user",
    )
    key_positives: list[str] = Field(
        default_factory=list,
        description="Positive aspects of the deal (max 3 bullet points)",
    )
    key_concerns: list[str] = Field(
        default_factory=list,
        description="Concerns or red flags (max 3 bullet points)",
    )