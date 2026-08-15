from fastapi.testclient import TestClient
from argus_api.main import app

client = TestClient(app)


def test_health_reports_no_automatic_jobs(monkeypatch):
    monkeypatch.delenv("ARGUS_DATABASE_URL", raising=False)
    assert client.get("/health").json()["automatic_jobs"] == "disabled"


def test_snapshot_fallback_is_unambiguously_demo(monkeypatch):
    monkeypatch.delenv("ARGUS_DATABASE_URL", raising=False)
    payload = client.get("/api/v1/public/market-snapshot").json()
    assert payload["environment"] == "DEMO"
    assert "not live" in payload["disclaimer"]
    assert all(item["freshness"] == "DEMO" for item in payload["observations"])
