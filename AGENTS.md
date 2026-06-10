# AGENTS.md

See `CLAUDE.md` for the primary architecture, commands, testing, and frontend breakdown. This file adds what CLAUDE.md does not cover.

## Files to read before making changes

- `DESIGN.md` — Stitch-generated design tokens (colors, typography, layout). Read before modifying frontend pages to stay on-brand.
- `IMPROVEMENTS.md` — roadmapped features (health check, caching, rate limiting, etc.). Check before adding unrelated improvements.

## Environment quirks

- `load_dotenv()` in `main.py` must run before `from database import ...` — the import triggers engine construction that reads `DATABASE_URL`. This order is enforced by `# noqa: E402` placement.
- Only `GEMINI_API_KEY` is needed. No OpenAI config exists anymore.

## Dev server

Must run from inside `app/` because the Jinja2 templates dir is a relative path `"templates"`:
```
cd app && uv run fastapi dev main.py
```
Static files use `Path(__file__).parent` so they are CWD-independent.

## Schema changes

SQLite `Base.metadata.create_all` only creates missing tables — it does **not** alter existing columns. If you rename or remove a column in a model, delete `app/lingora.db` to recreate it. Alembic is a dependency but not wired up; add migrations before production.

## Production

`gunicorn` is a dependency but no config or startup script exists. Before deploying, add a `gunicorn.conf.py` or invocation. Likely use `gunicorn -k uvicorn.workers.UvicornWorker main:app`.

## No CI, no pre-commit

No CI workflow (`.github/workflows/`), no pre-commit hooks. Run checks manually:
```
uv run ruff check . && uv run ruff format . --check && uv run ty check && uv run pytest
```
