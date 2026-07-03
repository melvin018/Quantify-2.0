"""
test_chatbot.py

Tests for the Quantify backend. Covers query parsing, mock data, and the
FastAPI endpoints (using FastAPI's TestClient, no live server needed).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from fastapi.testclient import TestClient

from app.services import query_parser, mock_data
from app.main import app

client = TestClient(app)


# ---------- query_parser tests ----------

def test_extract_known_symbol():
    assert "AAPL" in query_parser.extract_symbols("What is the price of AAPL?")


def test_extract_dollar_prefixed_symbol():
    assert "XYZ" in query_parser.extract_symbols("How is $XYZ doing?")


def test_extract_no_false_positives_on_common_words():
    symbols = query_parser.extract_symbols("Tell me about the dividend yield for MSFT")
    assert "TELL" not in symbols
    assert "YIELD" not in symbols
    assert "MSFT" in symbols


def test_classify_intent_overview():
    assert query_parser.classify_intent("What is the market cap of AAPL?") == "overview"


def test_classify_intent_quote():
    assert query_parser.classify_intent("What is the price of AAPL?") == "quote"


# ---------- mock_data tests ----------

def test_mock_quote_has_required_fields():
    quote = mock_data.get_mock_quote("AAPL")
    for field in ("symbol", "price", "change", "change_percent", "volume", "source"):
        assert field in quote
    assert quote["source"] == "mock_data"


def test_mock_overview_unknown_symbol_uses_default():
    overview = mock_data.get_mock_overview("ZZZZ")
    assert overview["name"] == "Unknown Company"


# ---------- API endpoint tests ----------

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_chat_endpoint_returns_expected_shape():
    resp = client.post("/api/chat", json={"question": "What is the price of AAPL?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "symbols" in data
    assert "AAPL" in data["symbols"]
    assert data["intent"] == "quote"


def test_chat_endpoint_no_symbol_in_question():
    resp = client.post("/api/chat", json={"question": "How are markets doing today?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbols"] == []
