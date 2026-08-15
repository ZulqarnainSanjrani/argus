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


def test_demo_home_contract_is_complete_and_unambiguous():
    response = client.get("/api/v1/demo/home")
    assert response.status_code == 200
    payload = response.json()
    assert payload["environment"] == "DEMO"
    assert "not live" in payload["disclaimer"]
    assert payload["fixture_source"].startswith("ARGUS synthetic")
    assert len(payload["rates"]) >= 6
    assert {rate["tenor"] for rate in payload["rates"]} >= {"3M", "1Y", "10Y"}
    assert payload["events"]
    assert payload["source_health"][-1]["status"] == "DISABLED"
