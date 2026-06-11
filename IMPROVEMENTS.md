# LINGORA IMPROVEMENTS

A. Health check + LLM provider health check
- /health endpoint: returns {"status": "ok", "db": "ok", "provider": "ok"} 
- Pings DB and runs a tiny test translation (or just checks the provider client is constructable)
- For load balancers, uptime monitors, k8s liveness probes
- Effort: 15 min. Robustness: essential for prod.

B. Translation cache (idempotency for repeated text+language combos)
- Hash text + sorted_languages to get a cache key
- If a recent completed translation exists with the same text and language subset, return its results instead of re-calling LLM
- Saves $$ on LLM costs, makes repeated translations instant
- Effort: 30 min. Robustness: $$$, speed, idempotency.

C. Input validation + size limits
- Cap text length (e.g., 5000 chars per translation, 10 languages max)
- Validate language list (non-empty, no duplicates, max 10)
- Pydantic validators on the request schema
- Returns 422 with clear error message
- Effort: 10 min. Robustness: prevents abuse, LLM cost blowup, DB bloat.

D. Structured request logging with request ID
- Middleware that generates a request ID, attaches to logger
- All logs during the request include the ID
- Returns the request ID in response header (X-Request-ID)
- Effort: 20 min. Robustness: debuggability of async background tasks.

E. Timeout on LLM calls
- Add asyncio.wait_for(translate_text(...), timeout=30)
- On timeout, mark request as "failed" with reason
- Effort: 10 min. Robustness: prevents stuck background tasks.

F. Retry with exponential backoff for transient LLM errors
- 429, 5xx → retry 3 times with backoff (1s, 2s, 4s)
- Non-retryable errors fail immediately
- Effort: 30 min. Robustness: handles provider hiccups.

G. Rate limiting with slowapi
- 10 requests/minute per IP on /translate
- Returns 429 with Retry-After
- Effort: 15 min. Robustness: prevents abuse.

H. API documentation
- FastAPI auto-generates /docs (Swagger UI) — already there by default
- Add a /api example endpoint to show how to call /translate programmatically
- Effort: 5 min for the example endpoint. Low robustness.
