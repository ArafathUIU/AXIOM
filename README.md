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
