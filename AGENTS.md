# AGENTS.md

See `CLAUDE.md` for the primary architecture, commands, testing, and frontend breakdown. This file adds what CLAUDE.md does not cover.

## Dead code to avoid

`models.IndividualTranslations` (`app/models.py:59`) is unused. No route or function writes to it. `process_translations` writes to `TranslationResult`. Do not reference `IndividualTranslations` in new code; consider removing it.

## Files to read before making changes

- `DESIGN.md` — Stitch-generated design tokens (colors, typography, layout). Read before modifying frontend pages to stay on-brand.
- `IMPROVEMENTS.md` — roadmapped features (health check, caching, rate limiting, etc.). Check before adding unrelated improvements.

## Environment quirks

- `.env.example` says `TRANSLATION_PROVIDER=openai` but the code default is `gemini` (`app/utils.py:33`). Trust the code, not the example.
- `load_dotenv()` in `main.py` must run before `from database import ...` — the import triggers engine construction that reads `DATABASE_URL`. This order is enforced by `# noqa: E402` placement.

## Dev server

Must run from inside `app/` because the Jinja2 templates dir is a relative path `"templates"`:
```
cd app && uv run fastapi dev main.py
```
Static files use `Path(__file__).parent` so they are CWD-independent.

## Production

`gunicorn` is a dependency but no config or startup script exists. Before deploying, add a `gunicorn.conf.py` or invocation. Likely use `gunicorn -k uvicorn.workers.UvicornWorker main:app`.

## No CI, no pre-commit

No CI workflow (`.github/workflows/`), no pre-commit hooks. Run checks manually:
```
uv run ruff check . && uv run ruff format . --check && uv run ty check && uv run pytest
```
