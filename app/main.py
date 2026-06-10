"""
Script Name : main.py
Description : Main FastAPI application setup and route definitions.
Author      : @tonybnya
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()

# Local imports (must come after load_dotenv so engine construction picks up env)
from database import engine, get_db, SessionLocal  # noqa: E402
from schemas import TranslationRequestSchema  # noqa: E402
import models  # noqa: E402
from utils import process_translations  # noqa: E402

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (use absolute path so it works regardless of CWD)
_STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

# Templates configuration
templates = Jinja2Templates(directory="templates")


# Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    """Custom handler for 404 errors to render a template."""
    if exc.status_code == 404:
        return templates.TemplateResponse(
            request=request, name="404.html", status_code=404
        )
    return exc


# Page Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Renders the landing page."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
        status_code=200,
    )


@app.get("/translator", response_class=HTMLResponse)
async def translator(request: Request):
    """Renders the translator interface page."""
    return templates.TemplateResponse(
        request=request,
        name="translator.html",
        context={"request": request},
        status_code=200,
    )


# API Endpoints
@app.get("/health", status_code=200)
def health() -> dict[str, str]:
    """API health check endpoint. Pings DB and checks provider config."""
    db_status = "ok"
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    provider_status = "ok" if os.getenv("GEMINI_API_KEY") else "unconfigured"

    status = "ok" if db_status == "ok" and provider_status == "ok" else "degraded"

    return {
        "service": "Lingora API",
        "status": status,
        "db": db_status,
        "provider": provider_status,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/translate")
async def translate(
    request_data: TranslationRequestSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Receives a translation request and queues it for processing."""
    logging.info(f"Received translation request: {request_data}")

    db_request = models.TranslationRequest(
        text=request_data.text,
        languages=request_data.languages,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Enqueue the heavy LLM work. process_translations owns its own DB
    # session because BackgroundTasks run after the request response
    # is sent (and the request-scoped session has already been closed).
    background_tasks.add_task(
        process_translations,
        db_request.id,
        request_data.text,
        [lang.strip() for lang in request_data.languages.split(",") if lang.strip()],
    )

    return {
        "id": db_request.id,
        "status": db_request.status,
        "message": "Translation request accepted and is being processed.",
    }


@app.get("/translate/{request_id}")
async def get_translation_status(request_id: int, db: Session = Depends(get_db)):
    """Retrieves the status and results of a translation request."""
    request_obj = (
        db.query(models.TranslationRequest)
        .filter(models.TranslationRequest.id == request_id)
        .first()
    )
    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found")

    if request_obj.status in {"in progress", "failed"}:
        return {"id": request_id, "status": request_obj.status}

    translations = (
        db.query(models.TranslationResult)
        .filter(models.TranslationResult.request_id == request_id)
        .all()
    )
    return {
        "id": request_id,
        "status": request_obj.status,
        "translations": [
            {"language": t.language, "translated_text": t.translated_text}
            for t in translations
        ],
    }
