# Deployment

AXIOM can run anywhere that supports a Python web process. The production path is Docker with a managed PostgreSQL database.

## Environment

Set these variables in production:

- `DATABASE_URL`: PostgreSQL connection string
- `CORS_ORIGINS`: comma-separated allowed frontend origins, or `*`
- `ENABLE_RATE_LIMITING`: `true` or `false`
- `IP_RATE_LIMIT_PER_MINUTE`: per-IP request budget
- `API_KEY_RATE_LIMIT_PER_MINUTE`: per-key request budget
- `REDIS_URL`: reserved for a future distributed rate-limit backend
- `GEMINI_API_KEY`: optional Gemini API key for replacing local insight summaries
- `ADMIN_TOKEN`: token required for admin mutations such as creating API keys, persisting anomalies, and generating insights

## Docker

```bash
docker build -t axiom .
docker run -p 8000:8000 --env DATABASE_URL=sqlite:///./axiom.db axiom
```

## Railway

1. Create a Railway project from the GitHub repository.
2. Add a PostgreSQL database service.
3. Set `DATABASE_URL` to the Railway PostgreSQL connection string.
4. Deploy with the included `Dockerfile`.
5. Open `/health`, `/dashboard`, and `/docs` after deploy.
6. Set `ADMIN_TOKEN` before exposing the service publicly.
