"""
query_parser.py

Lightweight intent + entity extraction for incoming questions: figures out
which stock symbol(s) the user is asking about and what kind of data they
need (price quote vs. company fundamentals) before calling the financial
data service. This mirrors the role Dialogflow played in the original
architecture (intent classification + entity extraction) but implemented
directly in Python so it requires no external account/service to run.

For a closer match to the original architecture, this logic could be
moved into a Dialogflow agent's intent/entity config, with this module's
functions becoming the webhook fulfillment handlers. See README for notes
on wiring that up.
"""

import re

_KNOWN_SYMBOLS = {"AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "AMD", "NVDA"}

_OVERVIEW_KEYWORDS = [
    "market cap", "p/e", "pe ratio", "dividend", "eps", "earnings per share",
    "sector", "fundamentals", "overview", "52 week", "52-week",
]


def extract_symbols(text: str) -> list:
    """
    Finds stock ticker symbols in free text.

    Trusts two signals only:
      1. Known symbols from our reference list (_KNOWN_SYMBOLS)
      2. $-prefixed tokens (e.g. "$XYZ"), which is an unambiguous signal
         of ticker intent regardless of list membership

    Earlier versions of this function also matched bare uppercase 2-5
    letter words as a fallback, but that produced too many false
    positives ("TELL", "YIELD", "PRICE", etc. all match that shape once a
    sentence is upper-cased) for a stopword list to keep up with. A real
    production system would use a proper NER model or a maintained ticker
    database with fuzzy matching against company names; this demo keeps
    the simpler, more conservative two-signal approach instead and
    accepts that obscure tickers without a $ prefix won't be caught.
    """
    text_upper = text.upper()
    found = set()

    for symbol in _KNOWN_SYMBOLS:
        if re.search(rf"\b{symbol}\b", text_upper):
            found.add(symbol)

    for match in re.finditer(r"\$([A-Z]{1,5})\b", text_upper):
        found.add(match.group(1))

    return list(found)


def classify_intent(text: str) -> str:
    """Returns 'overview' for fundamentals questions, 'quote' otherwise."""
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in _OVERVIEW_KEYWORDS):
        return "overview"
    return "quote"


def parse_query(text: str) -> dict:
    return {
        "symbols": extract_symbols(text),
        "intent": classify_intent(text),
        "raw_text": text,
    }
