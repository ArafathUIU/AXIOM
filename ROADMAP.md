# AXIOM Roadmap

AXIOM is being built as a lightweight, self-hosted API observability engine. The current backend already captures request traffic and exposes basic analytics. The remaining work is organized into small, shippable phases so each change can be reviewed, tested, and deployed independently.

## Current Foundation

- FastAPI application with health and root endpoints
- SQLAlchemy database setup with SQLite defaults for local development
- Automatic request logging middleware
- Request log persistence for method, path, status code, response time, client IP, user agent, and timestamp
- Recent request log API
- Analytics APIs for summary metrics, endpoint usage, and status-code distribution
- Pytest coverage for the implemented foundation

## Phased Delivery Plan

1. Document the implementation roadmap.
2. Add environment example and configuration documentation.
3. Harden application settings for local and production environments.
4. Add database migration tooling foundation.
5. Add pagination metadata for request logs.
6. Add request log filtering by method, status code, and path.
7. Add request log filtering by time range.
8. Add single request log detail endpoint.
9. Add analytics time-window query support.
10. Add slowest endpoints analytics.
11. Add top error endpoints analytics.
12. Add traffic-over-time analytics.
13. Add status-code family analytics.
14. Add latency percentile analytics.
15. Add anomaly detection service foundation.
16. Add slow-response anomaly detection.
17. Add error-spike anomaly detection.
18. Add traffic-burst anomaly detection.
19. Persist detected anomalies.
20. Add anomaly listing API.
21. Add anomaly summary API.
22. Add API key persistence model.
23. Add API key creation endpoint.
24. Add API key revocation endpoint.
25. Add API key authentication middleware.
26. Add API key usage tracking.
27. Add API-key-level analytics.
28. Add per-IP rate limiting foundation.
29. Add per-API-key rate limiting.
30. Add Redis configuration support.
31. Add in-memory development fallback for rate limits.
32. Add rate-limit response headers.
33. Add rate-limit test coverage.
34. Add AI insight configuration placeholders.
35. Add log summarization service interface.
36. Add Claude/Anthropic client integration.
37. Add AI insight endpoint.
38. Persist generated AI insights.
39. Add AI insight history endpoint.
40. Add dashboard summary endpoint.
41. Improve OpenAPI descriptions and tags.
42. Add global exception handling.
43. Add structured application logging.
44. Add CORS configuration.
45. Add Dockerfile.
46. Add Docker Compose for local development.
47. Add production database documentation.
48. Add CI test workflow.
49. Add Railway deployment documentation.
50. Final cleanup, full test pass, and README refresh.

## Delivery Rules

- Keep each phase small and independently useful.
- Prefer minimal changes that extend the current architecture.
- Add or update tests when behavior changes.
- Commit and push each phase separately with a clear message.
