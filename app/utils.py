"""
Script Name : utils.py
Description : Utility functions for translation and database operations.
Author      : @tonybnya
"""
import os
import logging
from typing import List

# Third-party
import openai as openai_client
import google.generativeai as genai
from sqlalchemy.orm import Session

# Local
from .models import TranslationRequest, TranslationResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
#  Provider configuration
# ---------------------------------------------------------------------------
_PROVIDER = os.getenv("TRANSLATION_PROVIDER", "openai").lower()  # "openai" or "gemini"

if _PROVIDER == "openai":
    openai_client.api_key = os.getenv("OPENAI_API_KEY")
elif _PROVIDER == "gemini":
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
else:
    raise ValueError(f"Unsupported TRANSLATION_PROVIDER: {_PROVIDER}")


async def translate_text(text: str, language: str) -> str:
    """Translate *text* into *language* using the configured LLM provider."""
    if _PROVIDER == "openai":
        return await _translate_openai(text, language)
    return await _translate_gemini(text, language)


# ---------------------------------------------------------------------------
#  OpenAI
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
#  Gemini
# ---------------------------------------------------------------------------
async def _translate_gemini(text: str, language: str) -> str:
    model = genai.GenerativeModel("gemini-pro")
    prompt = (
        f"You are a helpful assistant that translates text. "
        f"Translate the following text to {language}:\n\n{text}"
    )
    response = await model.generate_content_async(prompt)
    return response.text.strip()


# ---------------------------------------------------------------------------
#  Orchestration
# ---------------------------------------------------------------------------
async def process_translations(
    request_id: int,
    text: str,
    languages: List[str],
    db: Session,
) -> None:
    """Translate *text* into each *language* and persist results."""
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
        raise
