"""
Script Name : test_translate.py
Description : Tests for the /translate endpoint and background task pipeline.
Author      : @tonybnya
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


POLL_TIMEOUT_S = 5.0
POLL_INTERVAL_S = 0.1


def _wait_for_terminal_status(client, request_id: int, db_session) -> dict:
    """Poll /translate/{id} until status is 'completed' or 'failed'."""
    deadline = time.time() + POLL_TIMEOUT_S
    last_data = {}
    while time.time() < deadline:
        resp = client.get(f"/translate/{request_id}")
        assert resp.status_code == 200, resp.text
        last_data = resp.json()
        if last_data.get("status") in {"completed", "failed"}:
            return last_data
        time.sleep(POLL_INTERVAL_S)
    pytest.fail(
        f"Request #{request_id} never reached a terminal status within "
        f"{POLL_TIMEOUT_S}s. Last data: {last_data}"
    )


def test_translate_completes_when_provider_succeeds(client, db_session):
    """POST /translate should enqueue work; status must reach 'completed'."""
    from models import TranslationRequest, TranslationResult

    fake_translate = AsyncMock(side_effect=lambda text, lang: f"[{lang}] {text}")
    with patch("utils.translate_text", fake_translate):
        resp = client.post(
            "/translate",
            json={"text": "Hello, world!", "languages": "french, german"},
        )

    assert resp.status_code == 200
    payload = resp.json()
    assert "id" in payload
    assert payload["status"] in {"in progress", "completed"}

    request_id = payload["id"]
    final = _wait_for_terminal_status(client, request_id, db_session)
    assert final["status"] == "completed", final
    assert len(final["translations"]) == 2
    by_lang = {t["language"]: t["translated_text"] for t in final["translations"]}
    assert by_lang == {
        "french": "[french] Hello, world!",
        "german": "[german] Hello, world!",
    }

    # Verify rows were actually persisted
    db_request = db_session.query(TranslationRequest).filter_by(id=request_id).first()
    assert db_request is not None
    assert db_request.status == "completed"
    rows = db_session.query(TranslationResult).filter_by(request_id=request_id).all()
    assert len(rows) == 2


def test_translate_marks_failed_when_provider_raises(client, db_session):
    """If the LLM call fails, status must reach 'failed' (not stay 'in progress')."""
    from models import TranslationRequest

    fake_translate = AsyncMock(side_effect=RuntimeError("gemini down"))
    with patch("utils.translate_text", fake_translate):
        resp = client.post(
            "/translate",
            json={"text": "boom", "languages": "french"},
        )

    assert resp.status_code == 200
    request_id = resp.json()["id"]

    final = _wait_for_terminal_status(client, request_id, db_session)
    assert final["status"] == "failed", final

    db_request = db_session.query(TranslationRequest).filter_by(id=request_id).first()
    assert db_request is not None
    assert db_request.status == "failed"


def test_translate_uses_openai_v1_api(client, db_session, monkeypatch):
    """When TRANSLATION_PROVIDER=openai, must use the v1.x async client.

    Regression: the previous code called ``openai_client.ChatCompletion.acreate``
    which was removed in openai>=1.0.0.
    """
    from models import TranslationResult

    monkeypatch.setenv("TRANSLATION_PROVIDER", "openai")

    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="bonjour"))]
    fake_client = MagicMock()
    fake_client.chat.completions.create = AsyncMock(return_value=fake_response)
    fake_constructor = MagicMock(return_value=fake_client)

    with patch("utils.AsyncOpenAI", fake_constructor, create=True):
        resp = client.post(
            "/translate",
            json={"text": "morning", "languages": "french"},
        )

    assert resp.status_code == 200
    request_id = resp.json()["id"]
    final = _wait_for_terminal_status(client, request_id, db_session)
    assert final["status"] == "completed", final
    assert final["translations"][0]["translated_text"] == "bonjour"

    # The v1.x async client was actually called
    fake_constructor.assert_called_once()
    fake_client.chat.completions.create.assert_awaited_once()
    call_kwargs = fake_client.chat.completions.create.await_args.kwargs
    assert call_kwargs["model"] == "gpt-4"
    assert {"role": "user", "content": "morning"} in call_kwargs["messages"]

    # Result was persisted
    rows = db_session.query(TranslationResult).filter_by(request_id=request_id).all()
    assert len(rows) == 1
    assert rows[0].language == "french"
    assert rows[0].translated_text == "bonjour"
