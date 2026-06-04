"""
Script Name : utils.py
Description : Utility functions for translation and database operations.
Author      : @tonybnya
"""

import os
import logging
from datetime import datetime
from typing import List

# Third-party
import openai as openai_client
from google import genai

# Local
from database import SessionLocal
from models import TranslationRequest, TranslationResult

logger = logging.getLogger(__name__)

#  Provider configuration
_PROVIDER = os.getenv("TRANSLATION_PROVIDER", "gemini").lower()  # "openai" or "gemini"

if _PROVIDER == "openai":
    openai_client.api_key = os.getenv("OPENAI_API_KEY")
elif _PROVIDER == "gemini":
    # The new google-genai SDK uses a single Client instance.
    _gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
else:
    raise ValueError(f"Unsupported TRANSLATION_PROVIDER: {_PROVIDER}")


async def translate_text(text: str, language: str) -> str:
    """Translate *text* into *language* using the configured LLM provider."""
    if _PROVIDER == "openai":
        return await _translate_openai(text, language)
    return await _translate_gemini(text, language)


#  OpenAI
async def _translate_openai(text: str, language: str) -> str:
    response = await openai_client.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that translates text. "
                f"Translate the following text to {language}:",
            },
            {"role": "user", "content": text},
        ],
    )
    return response["choices"][0]["message"]["content"].strip()


#  Gemini (using the new google-genai SDK)
async def _translate_gemini(text: str, language: str) -> str:
    prompt = (
        f"You are a helpful assistant that translates text. "
        f"Translate the following text to {language}:\n\n{text}"
    )
    response = await _gemini_client.aio.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()


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
            request.updated_at = datetime.utcnow()
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
                request.updated_at = datetime.utcnow()
                db.commit()
        except Exception:
            db.rollback()
    finally:
        db.close()
