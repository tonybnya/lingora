"""
Script Name : test_translate.py
Description : Tests for the /translate endpoint and background task pipeline.
Author      : @tonybnya
"""

import time
from unittest.mock import AsyncMock, patch

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
