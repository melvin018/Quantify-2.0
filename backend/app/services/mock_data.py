"""
mock_data.py

Realistic mock financial data used when no Alpha Vantage API key is set
(e.g. for local demos or this sandbox). This lets the chatbot demonstrate
its full reasoning pipeline -- retrieving data, then having the LLM reason
over it -- without requiring a live API key.

Data here is illustrative, not real-time market data, and is clearly
labeled as such in every response (see "source": "mock_data").
"""

import random

_MOCK_COMPANIES = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology", "base_price": 195.50},
    "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "base_price": 415.20},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "base_price": 165.80},
    "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "base_price": 178.30},
    "TSLA": {"name": "Tesla Inc.", "sector": "Consumer Discretionary", "base_price": 248.90},
    "AMD": {"name": "Advanced Micro Devices Inc.", "sector": "Technology", "base_price": 152.40},
    "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology", "base_price": 124.60},
}

_DEFAULT_COMPANY = {"name": "Unknown Company", "sector": "Unknown", "base_price": 100.00}


def get_mock_quote(symbol: str) -> dict:
    symbol = symbol.upper().strip()
    company = _MOCK_COMPANIES.get(symbol, _DEFAULT_COMPANY)

    # Deterministic-ish pseudo-variation per symbol so repeated calls in a
    # demo are stable-ish but not perfectly static.
    rng = random.Random(symbol)
    change = round(rng.uniform(-5, 5), 2)
    price = round(company["base_price"] + change, 2)
    change_percent = round((change / company["base_price"]) * 100, 2)

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "change_percent": f"{change_percent}%",
        "volume": rng.randint(20_000_000, 90_000_000),
        "source": "mock_data",
    }


def get_mock_overview(symbol: str) -> dict:
    symbol = symbol.upper().strip()
    company = _MOCK_COMPANIES.get(symbol, _DEFAULT_COMPANY)
    rng = random.Random(symbol + "overview")

    return {
        "symbol": symbol,
        "name": company["name"],
        "sector": company["sector"],
        "market_cap": f"{rng.randint(50, 3000)}B",
        "pe_ratio": round(rng.uniform(12, 45), 1),
        "eps": round(rng.uniform(2, 15), 2),
        "dividend_yield": f"{round(rng.uniform(0, 2.5), 2)}%",
        "52_week_high": round(company["base_price"] * 1.25, 2),
        "52_week_low": round(company["base_price"] * 0.75, 2),
        "source": "mock_data",
    }
