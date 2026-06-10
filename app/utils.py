"""
Script Name : utils.py
Description : Utility functions for translation and database operations.
Author      : @tonybnya
"""

import logging
from datetime import datetime, timezone
from typing import List

from google import genai

from database import SessionLocal
from models import TranslationRequest, TranslationResult

logger = logging.getLogger(__name__)

_gemini_client: genai.Client | None = None


def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        import os

        _gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _gemini_client


async def translate_text(text: str, language: str) -> str:
    client = _get_gemini_client()
    prompt = (
        f"You are an expert translator. "
        f"Translate the following text to {language}. "
        f"Return ONLY the translated text, without any additional comments, explanation, or quotes:\n\n{text}"
    )
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return (response.text or "").strip()


#  Orchestration
async def process_translations(
    request_id: int,
    text: str,
    languages: List[str],
) -> None:
    """Translate *text* into each *language* and persist results.

    Owns its own DB session. Background tasks run after the FastAPI request
    response is sent, so we cannot rely on the request-scoped session from
    ``Depends(get_db)`` — it would be closed by the time we got here.
    """
    db = SessionLocal()
    try:
        for language in languages:
            translated_text = await translate_text(text, language)

            result = TranslationResult(
                request_id=request_id,
                language=language,
                translated_text=translated_text,
            )
            db.add(result)
            db.commit()

        # Mark parent request as completed
        request = (
            db.query(TranslationRequest)
            .filter(TranslationRequest.id == request_id)
            .first()
        )
        if request:
            request.status = "completed"
            request.updated_at = datetime.now(timezone.utc)
            db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("Translation processing failed: %s", exc, exc_info=True)
        # Flip the request to "failed" so the frontend stops polling
        # instead of getting stuck at 75% forever. The response has
        # already been sent by the time we get here, so re-raising would
        # only crash the background task runner (and surprise the caller
        # in tests); logging is the right signal in production.
        try:
            request = (
                db.query(TranslationRequest)
                .filter(TranslationRequest.id == request_id)
                .first()
            )
            if request:
                request.status = "failed"
                request.updated_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            db.rollback()
    finally:
        db.close()
