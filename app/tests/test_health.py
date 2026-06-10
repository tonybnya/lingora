"""
Script Name : test_health.py
Description : Tests for the /health endpoint.
Author      : @tonybnya
"""


def test_health_returns_expected_shape(client, db_session):
    """GET /health should return the standard status envelope."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()

    assert body["service"] == "Lingora API"
    assert body["status"] in {"ok", "degraded"}
    assert body["db"] in {"ok", "error"}
    assert body["provider"] in {"ok", "unconfigured", "error"}
    assert "timestamp" in body


def test_health_db_ping(client, db_session):
    """Database should report ok when the test DB is available."""
    resp = client.get("/health")
    assert resp.json()["db"] == "ok"
