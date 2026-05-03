# AXIOM Roadmap

AXIOM is being built as a lightweight, self-hosted API observability engine. The current backend already captures request traffic and exposes basic analytics. The remaining work is organized into small, shippable phases so each change can be reviewed, tested, and deployed independently.

## Current Foundation

- FastAPI application with health, root, dashboard, logs, analytics, anomaly, API key, and insight endpoints
- SQLAlchemy database setup with SQLite defaults for local development and Alembic migration metadata
- Automatic request logging middleware with request log persistence
- Logs API with pagination, filtering, time ranges, recent logs, and detail lookup
- Analytics APIs for summary metrics, endpoint usage, slow/error endpoints, traffic buckets, latency percentiles, and status codes
- Rule-based anomaly detection with preview, persistence, listing, and summaries
- API key creation, revocation, usage tracking, and in-memory rate limiting
- Gemini-backed insight generation with deterministic local fallback
- Static dashboard with live metrics, logs, anomalies, status codes, and insight generation
- Docker, Docker Compose, GitHub Actions tests, and deployment documentation

## Phased Delivery Plan

1. Completed: Document the implementation roadmap.
2. Completed: Add environment example and configuration documentation.
3. Completed: Harden application settings for local and production environments.
4. Completed: Add database migration tooling foundation.
5. Completed: Add pagination metadata for request logs.
6. Completed: Add request log filtering by method, status code, and path.
7. Completed: Add request log filtering by time range.
8. Completed: Add single request log detail endpoint.
9. Completed: Add analytics time-window query support.
10. Completed: Add slowest endpoints analytics.
11. Completed: Add top error endpoints analytics.
12. Completed: Add traffic-over-time analytics.
13. Completed: Add status-code family analytics.
14. Completed: Add latency percentile analytics.
15. Completed: Add anomaly detection service foundation.
16. Completed: Add slow-response anomaly detection.
17. Completed: Add error-spike anomaly detection.
18. Completed: Add traffic-burst anomaly detection.
19. Completed: Persist detected anomalies.
20. Completed: Add anomaly listing API.
21. Completed: Add anomaly summary API.
22. Completed: Add API key persistence model.
23. Completed: Add API key creation endpoint.
24. Completed: Add API key revocation endpoint.
25. Completed: Add API key authentication middleware.
26. Completed: Add API key usage tracking.
27. Completed: Add API-key-level analytics.
28. Completed: Add per-IP rate limiting foundation.
29. Completed: Add per-API-key rate limiting.
30. Completed: Add Redis configuration support placeholder.
31. Completed: Add in-memory development fallback for rate limits.
32. Completed: Add rate-limit response headers.
33. Completed: Add rate-limit test coverage.
34. Completed: Add AI insight configuration placeholders.
35. Completed: Add log summarization service interface.
36. Completed: Add Gemini client integration.
37. Completed: Add AI insight endpoint.
38. Completed: Persist generated AI insights.
39. Completed: Add AI insight history endpoint.
40. Completed: Add dashboard summary endpoint.
41. Completed: Improve OpenAPI descriptions and tags.
42. Completed: Add global exception handling.
43. Completed: Add structured application logging.
44. Completed: Add CORS configuration.
45. Completed: Add Dockerfile.
46. Completed: Add Docker Compose for local development.
47. Completed: Add production database documentation.
48. Completed: Add CI test workflow.
49. Completed: Add Railway deployment documentation.
50. Completed: Final cleanup, full test pass, and README refresh.

## Future Enhancements

- Replace in-memory rate limiting with Redis-backed distributed rate limits.
- Add role-based user accounts for multi-user administration.
- Add hosted deployment screenshots and public demo URL.
- Add PostgreSQL-specific integration testing.

## Delivery Rules

- Keep each phase small and independently useful.
- Prefer minimal changes that extend the current architecture.
- Add or update tests when behavior changes.
- Commit and push each phase separately with a clear message.
