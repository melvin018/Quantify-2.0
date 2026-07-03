"""
alpha_vantage_client.py

Real client for the Alpha Vantage financial data API. Requires an API key
(free tier available at https://www.alphavantage.co/support/#api-key).

Set ALPHA_VANTAGE_API_KEY in your .env file to use this. If no key is set,
get_quote() and get_company_overview() fall back to realistic mock data
(see mock_data.py) so the rest of the app keeps working in a demo/dev
environment without requiring a live key.
"""

import os
import requests
from app.services import mock_data

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"


def _get_api_key():
    return os.environ.get("ALPHA_VANTAGE_API_KEY", "").strip()


def get_quote(symbol: str) -> dict:
    """
    Returns the latest quote for a stock symbol:
    { symbol, price, change, change_percent, volume }

    Real endpoint: GLOBAL_QUOTE
    Docs: https://www.alphavantage.co/documentation/#latestprice
    """
    api_key = _get_api_key()
    symbol = symbol.upper().strip()

    if not api_key:
        return mock_data.get_mock_quote(symbol)

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": api_key,
    }

    try:
        resp = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("Global Quote", {})

        if not data:
            # Alpha Vantage returns an empty object for invalid symbols
            # or when the rate limit is hit -- fall back to mock data
            # rather than returning a confusing empty response.
            return mock_data.get_mock_quote(symbol)

        return {
            "symbol": data.get("01. symbol", symbol),
            "price": float(data.get("05. price", 0)),
            "change": float(data.get("09. change", 0)),
            "change_percent": data.get("10. change percent", "0%"),
            "volume": int(data.get("06. volume", 0)),
            "source": "alpha_vantage_live",
        }
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Alpha Vantage request failed ({e}), falling back to mock data.")
        return mock_data.get_mock_quote(symbol)


def get_company_overview(symbol: str) -> dict:
    """
    Returns fundamental company data: name, sector, market cap, P/E ratio, etc.

    Real endpoint: OVERVIEW
    Docs: https://www.alphavantage.co/documentation/#company-overview
    """
    api_key = _get_api_key()
    symbol = symbol.upper().strip()

    if not api_key:
        return mock_data.get_mock_overview(symbol)

    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": api_key,
    }

    try:
        resp = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data or "Symbol" not in data:
            return mock_data.get_mock_overview(symbol)

        return {
            "symbol": data.get("Symbol", symbol),
            "name": data.get("Name", "Unknown"),
            "sector": data.get("Sector", "Unknown"),
            "market_cap": data.get("MarketCapitalization", "Unknown"),
            "pe_ratio": data.get("PERatio", "Unknown"),
            "eps": data.get("EPS", "Unknown"),
            "dividend_yield": data.get("DividendYield", "Unknown"),
            "52_week_high": data.get("52WeekHigh", "Unknown"),
            "52_week_low": data.get("52WeekLow", "Unknown"),
            "source": "alpha_vantage_live",
        }
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Alpha Vantage request failed ({e}), falling back to mock data.")
        return mock_data.get_mock_overview(symbol)
