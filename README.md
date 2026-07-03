# Quantify — Financial Q&A Chatbot

Ask plain-language questions about stocks ("What's AAPL trading at?", "Compare AMD and NVDA fundamentals") and get answers grounded in real financial data, powered by an LLM.

## Architecture

```
frontend/index.html  →  FastAPI backend  →  query_parser (intent + symbols)
                                          →  alpha_vantage_client (live or mock data)
                                          →  llm_service (Claude API or FLAN-T5)
                                          →  database (MySQL or SQLite) for chat history
```

- **Backend**: FastAPI (`backend/app/`)
- **Frontend**: Single-page HTML/CSS/JS (`frontend/index.html`) — no build step required
- **LLM**: Claude API by default; Google FLAN-T5-Large (via Hugging Face transformers) as an alternative backend
- **Financial data**: Alpha Vantage API, with realistic mock data as a fallback when no key is set
- **Database**: MySQL in production, SQLite automatically as a zero-setup fallback
- **CI/CD**: Jenkins pipeline (`jenkins/Jenkinsfile`) + Docker (`docker/`)

## Quick Start (zero configuration)

The app runs out of the box with **no API keys at all**, using mock financial data and reporting clearly when no LLM key is set.

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Then open `frontend/index.html` in a browser (or serve it: `cd frontend && python3 -m http.server 8080`).

## Enabling Live Answers

1. Copy `.env.example` to `.env`
2. Get an Anthropic API key at https://console.anthropic.com and set `ANTHROPIC_API_KEY`
3. (Optional) Get a free Alpha Vantage key at https://www.alphavantage.co/support/#api-key and set `ALPHA_VANTAGE_API_KEY` for live market data instead of mock data
4. Restart the backend

That's it — no code changes needed. The app detects the keys and switches from mock/no-LLM mode to fully live automatically.

## About the LLM Backend Choice

This project was originally architected around **Google FLAN-T5-Large**, run locally via Hugging Face `transformers`. That implementation is fully included and correct (`backend/app/services/llm_service.py`, `FlanT5LLM` class) — but it requires `torch` and several GB of disk space for the model weights, which isn't available in every environment (including the sandbox this was built in).

To make the chatbot actually runnable everywhere with zero extra setup, the default backend is the **Claude API** instead (`ClaudeLLM` class) — same interface, same prompt structure, just an API call instead of a local model. Switch between them with `LLM_BACKEND` in `.env`:

```
LLM_BACKEND=claude    # default, works immediately with an API key
LLM_BACKEND=flant5    # requires `pip install transformers torch` first
```

## Project Structure

```
quantify-chatbot/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app entry point
│       ├── routers/chat.py      # /api/chat and /api/history endpoints
│       └── services/
│           ├── query_parser.py        # extracts stock symbols + intent from text
│           ├── alpha_vantage_client.py # live financial data (with mock fallback)
│           ├── mock_data.py           # realistic demo data
│           ├── llm_service.py         # Claude API + FLAN-T5 backends
│           └── database.py            # MySQL/SQLite chat history
├── frontend/
│   └── index.html               # single-page chat UI
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml       # backend + MySQL + frontend, full stack
├── jenkins/
│   └── Jenkinsfile              # CI/CD pipeline: test → build → deploy
├── tests/
│   └── test_chatbot.py          # pytest suite (parser, mock data, API endpoints)
├── .env.example
└── requirements.txt (in backend/)
```

## Running with Docker

```bash
cp .env.example .env   # fill in your keys
cd docker
docker-compose up --build
```

This brings up the backend (port 8000), a MySQL instance (port 3306), and the frontend (port 8080).

## Running Tests

```bash
pip install -r backend/requirements.txt
pytest tests/ -v
```

10 tests covering query parsing (symbol extraction, intent classification), mock data generation, and the FastAPI endpoints.

## Design Notes

**Why a $-prefix or known-symbol list instead of matching any uppercase word as a ticker?** An earlier version of the symbol extractor matched any short uppercase word, which produced false positives constantly — "TELL", "YIELD", "PRICE" all look like tickers once a sentence is uppercased for matching. A real production system would use a proper NER model or a maintained ticker database; this project uses a more conservative two-signal approach (known list + explicit `$` prefix) instead, documented in `query_parser.py`.

**Why does the data layer fall back to SQLite/mock data instead of just failing without MySQL/a live API key?** So the app is genuinely runnable and demoable immediately, in any environment, without a multi-step infrastructure setup first — while being transparent about which mode it's in (the frontend visibly tags every answer `live data` or `demo data`).

## Tech Stack

Python, FastAPI, Claude API / Hugging Face Transformers (FLAN-T5), Alpha Vantage API, MySQL/SQLite, Docker, Jenkins, HTML/CSS/JavaScript
# Quantify-2.0
