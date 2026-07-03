"""
chat.py

Main chat endpoint. Pipeline:
  1. Parse the question (extract stock symbols + intent) -- query_parser.py
  2. Fetch relevant financial data -- alpha_vantage_client.py (live or mock)
  3. Pass question + data to the LLM for a natural-language answer -- llm_service.py
  4. Log the interaction -- database.py
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import query_parser, alpha_vantage_client, llm_service, database

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    symbols: list[str]
    intent: str
    data_source: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    parsed = query_parser.parse_query(request.question)
    symbols = parsed["symbols"]
    intent = parsed["intent"]

    context = {}
    data_source = "none"

    for symbol in symbols[:3]:  # cap to avoid excessive API calls per message
        if intent == "overview":
            result = alpha_vantage_client.get_company_overview(symbol)
        else:
            result = alpha_vantage_client.get_quote(symbol)
        context[symbol] = result
        data_source = result.get("source", "unknown")

    llm = llm_service.get_llm()
    answer = llm.answer(request.question, context)

    try:
        database.log_interaction(request.question, answer, symbols, intent)
    except Exception as e:
        # Logging failures shouldn't break the chat response itself
        print(f"Warning: failed to log interaction: {e}")

    return ChatResponse(
        answer=answer,
        symbols=symbols,
        intent=intent,
        data_source=data_source,
    )


@router.get("/history")
def history(limit: int = 20):
    return database.get_recent_history(limit)
