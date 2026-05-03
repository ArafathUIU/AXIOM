# AXIOM
### API Intelligence & Observability Monitor

> **"See everything. Understand anything."**

AXIOM is a lightweight, self-hosted API observability engine built with FastAPI. It logs your API traffic, detects anomalies, enforces rate limits, and uses AI to turn raw logs into plain-English insights — think a simplified Datadog or New Relic, built from scratch.

---

## Features

- **Request Logger** — Log every API hit: endpoint, response time, status code, timestamp
- **Analytics Engine** — Most-used endpoints, average response times, error rates
- **Anomaly Detection** — Real-time alerts for error spikes, slow responses, and traffic bursts
- **Rate Limiting** — Per-IP and per-API-key request throttling
- **API Key System** — Generate, track, and revoke API keys with per-key usage stats
- **AI Insight Layer** — Natural language analysis of your logs powered by Claude AI
- **Dashboard-ready JSON** — Structured responses designed for frontend visualization

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL (SQLite for dev) |
| ORM | SQLAlchemy |
| AI Layer | Claude API (Anthropic) |
| Rate Limiting | slowapi + Redis |
| Deployment | Docker + Railway |
| Testing | pytest |

---

## Local Development

Create a virtual environment and install dependencies:

```bash
py -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

Run the API locally:

```bash
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Optional local configuration can be copied from `.env.example` into `.env`:

```text
APP_NAME=AXIOM
APP_VERSION=0.1.0
ENVIRONMENT=local
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./axiom.db
```

`DATABASE_URL` defaults to a local SQLite database for development. Set it to a PostgreSQL connection string when running against a production database.

Open the API in your browser:

```text
http://127.0.0.1:8000/
```

Run tests:

```bash
.venv\Scripts\python -m pytest
```

Create a database migration after changing SQLAlchemy models:

```bash
.venv\Scripts\python -m alembic revision --autogenerate -m "describe schema change"
.venv\Scripts\python -m alembic upgrade head
```

Health check endpoint:

```text
GET /health
```

Recent request logs endpoint:

```text
GET /logs?limit=20&offset=0
GET /logs?method=GET&status_code=404&path=/api
GET /logs?start_time=2026-01-01T00:00:00&end_time=2026-01-02T00:00:00
GET /logs/recent?limit=20
```

AXIOM logs API requests automatically, excluding `/health` to avoid polluting traffic data with uptime checks.

Analytics endpoints:

```text
GET /analytics/summary
GET /analytics/endpoints?limit=20
GET /analytics/status-codes
```
