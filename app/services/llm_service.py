from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.models.listing import CarListing
from app.models.schemas import LLMRecommendation

# Must run before ChatOpenAI() below, so OPENAI_API_KEY is in env at module load.
load_dotenv()


# Configuration
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.3  # Lower = more consistent, higher = more creative

# Reusable instances (created once at module load)
llm = ChatOpenAI(model=LLM_MODEL, temperature=TEMPERATURE)
parser = JsonOutputParser(pydantic_object=LLMRecommendation)

# Continued in app/services/llm_service.py

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are an expert car buying advisor. Your job is to analyze 
a used car listing and provide clear, honest, actionable advice to the buyer.

You will receive:
- The car listing being analyzed (the "input car")
- A list of similar cars from the market (with prices)
- A pricing analysis (fair price range, deal quality)
- Detected risks (if any)

Provide a structured recommendation:
- summary: 2-3 sentence natural language assessment
- recommendation: one of "buy", "inspect_then_buy", "negotiate", "avoid"
- key_positives: up to 3 short bullet points highlighting strengths
- key_concerns: up to 3 short bullet points highlighting issues

Guidelines:
- Be honest. Don't sugar-coat risks.
- Don't repeat the raw data — interpret it.
- If price is suspiciously low, mention scam possibility.
- If car is old or high-mileage, mention maintenance considerations.
- Keep tone professional but accessible (no jargon).

{format_instructions}"""),
    ("human", """Analyze this car listing:

INPUT CAR:
{input_car}

SIMILAR CARS FROM MARKET:
{similar_cars}

PRICING ANALYSIS:
{pricing_analysis}

DETECTED RISKS:
{risks}

Provide your structured recommendation."""),
])

chain = prompt_template | llm | parser


def generate_recommendation(
    input_listing: CarListing,
    similar_listings: list[dict],
    deal_analysis: dict,
    current_year: int,
) -> dict:
    """
    Generate LLM-powered natural language recommendation.
    
    Args:
        input_listing: The car being analyzed
        similar_listings: Top N similar cars from vector store
        deal_analysis: Output of pricing_service.analyze_deal()
        current_year: Used for computing age (passed through)
    
    Returns:
        Validated LLMRecommendation as dict:
        {
            "summary": "...",
            "recommendation": "buy" | "inspect_then_buy" | ...,
            "key_positives": [...],
            "key_concerns": [...],
        }
    """
    input_car_text = (
        f"{input_listing.year} {input_listing.make} {input_listing.model}, "
        f"{input_listing.km} km, {input_listing.price} EUR "
        f"(age: {input_listing.age_in_years(current_year)} years, "
        f"km/year: {input_listing.km_per_year(current_year):.0f})"
    )

    similar_cars_text = "\n".join([
        f"{i+1}. {car['year']} {car['make']} {car['model']}, "
        f"{car['km']} km, {car['price']} EUR "
        f"(similarity: {car['similarity_score']:.2f})"
        for i, car in enumerate(similar_listings)
    ])

    pricing_text = (
        f"Fair price: {deal_analysis['fair_price']} EUR\n"
        f"Fair price range: {deal_analysis['fair_price_min']} - {deal_analysis['fair_price_max']} EUR\n"
        f"Deal quality: {deal_analysis['deal_quality']}"
    )

    if deal_analysis['risks']:
        risks_text = "\n".join([
            f"- [{r['severity'].upper()}] {r['type']}: {r['message']}"
            for r in deal_analysis['risks']
        ])
    else:
        risks_text = "No significant risks detected."

    # Invoke with all variables
    result = chain.invoke({
        "input_car": input_car_text,
        "similar_cars": similar_cars_text,
        "pricing_analysis": pricing_text,
        "risks": risks_text,
        "format_instructions": parser.get_format_instructions(),
    })

    return result