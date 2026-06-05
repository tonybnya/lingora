# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Lingora is a real-time translation service. FastAPI backend, server-rendered Jinja2 templates, vanilla JS frontend (GSAP + Three.js on the landing page, axios on the translator). Translation is LLM-backed with a pluggable provider (Gemini default, OpenAI optional). Note: `README.md` is stale — it says "FastAPI and GPT-4"; the provider is configurable and defaults to Gemini.

## Commands

Python is managed with `uv`; lint/format with `ruff`; type-check with `ty`; test with `pytest`.

```bash
# Run the dev server. Templates are loaded from a CWD-relative "templates" dir,
# so you MUST run from inside app/.
cd app && uv run fastapi dev main.py

# Tests (run from repo root — pytest config sets pythonpath/testpaths)
uv run pytest
uv run pytest app/tests/test_translate.py::test_translate_uses_openai_v1_api  # single test

# Lint / format / type-check
uv run ruff check .
uv run ruff format .
uv run ty check

# Rebuild Tailwind CSS (Tailwind v4 CLI; source is app/input.css)
npx @tailwindcss/cli -i app/input.css -o app/static/css/style.css
```

## Architecture

### Async translation pipeline (the core flow)

Translation is fire-and-forget via FastAPI `BackgroundTasks`, with the frontend polling for completion:

1. `POST /translate` (`app/main.py`) persists a `TranslationRequest` row with status `"in progress"`, then enqueues `process_translations` and returns immediately with the row id.
2. `process_translations` (`app/utils.py`) runs after the response is sent. It **opens its own `SessionLocal`** — it cannot use the request-scoped `Depends(get_db)` session because that's already closed by the time a background task runs. It translates into each language, persists a `TranslationResult` per language, then flips the request to `"completed"`. On any exception it rolls back and sets status `"failed"` (never re-raises — re-raising would crash the background runner and the response is already gone).
3. Frontend (`app/static/js/translator.js`) polls `GET /translate/{id}` until status is `"completed"` or `"failed"`. The status field is the contract between background work and the UI — leaving a request stuck at `"in progress"` hangs the client forever.

### Provider abstraction (`app/utils.py`)

`translate_text` dispatches on `TRANSLATION_PROVIDER` (env, default `gemini`). Provider clients are lazily constructed and **read env at call time**, not import time, so tests can switch providers per-test via `monkeypatch.setenv`. OpenAI path uses the v1.x `AsyncOpenAI` client (`client.chat.completions.create`) — there's a regression test guarding against the removed `ChatCompletion.acreate`.

### Data layer (`app/database.py`, `app/models.py`)

SQLAlchemy 2.0 declarative (`Mapped`/`mapped_column`). `DATABASE_URL` selects the backend — SQLite (`sqlite:///./lingora.db`) in dev, Postgres in prod. Timestamps use `_utcnow` (timezone-aware UTC) for `default`/`onupdate`. Alembic is a dependency but tables are also auto-created via `Base.metadata.create_all` at import time in both `main.py` and `models.py`.

### Import convention and why `# noqa: E402` is everywhere

Modules import each other by bare name (`from database import ...`, `from models import ...`), not `app.database`. This works because `pyproject.toml` sets `pythonpath = ["app"]` for pytest and `fastapi dev main.py` is run from inside `app/`. In `main.py`, `load_dotenv()` runs **before** the local imports so engine/client construction picks up env vars — hence the local imports are deliberately placed after it with `# noqa: E402`.

## Testing notes

`app/tests/conftest.py` sets `DATABASE_URL` to a temp SQLite file and stub API keys **before** importing app modules (module-level engine/client construction depends on this ordering). `reset_db` drops/recreates all tables between tests. The `client` fixture uses `TestClient`, under which `BackgroundTasks` run synchronously — but tests still poll `GET /translate/{id}` via `_wait_for_terminal_status` rather than asserting immediately. LLM calls are always mocked (`AsyncMock`); never hit a real provider in tests.

## Frontend

Three pages: `index.html` (landing, GSAP + Three.js via CDN), `translator.html` (axios polling UI), `404.html`. Each links its own hand-authored CSS under `app/static/css/` (`index.css`, `translator.css`, `404.css`) — these are not Tailwind output. `app/input.css` + `tailwind.config.js` exist for Tailwind v4 but are not wired into the page `<link>` tags; treat per-page CSS as the source of truth unless you intentionally migrate a page to the built `style.css`.
