"""
main.py

FastAPI application entry point for the Quantify financial Q&A chatbot.

Run locally:
    uvicorn app.main:app --reload --port 8000

Then open frontend/index.html in a browser, or POST to /api/chat directly:
    curl -X POST http://localhost:8000/api/chat \\
         -H "Content-Type: application/json" \\
         -d '{"question": "What is the price of AAPL?"}'
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat
from app.services import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(
    title="Quantify",
    description="Financial Q&A chatbot API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
def root():
    return {"status": "ok", "service": "Quantify financial Q&A chatbot"}


@app.get("/health")
def health():
    return {"status": "healthy"}
