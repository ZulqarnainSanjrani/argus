from fastapi.testclient import TestClient

from argus_api.main import app

client = TestClient(app)


def test_health_reports_demo_and_no_external_calls() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "DEMO", "external_calls": "disabled"}


def test_snapshot_is_unambiguously_demo() -> None:
    response = client.get("/api/v1/public/market-snapshot")
    assert response.status_code == 200
    payload = response.json()
    assert payload["environment"] == "DEMO"
    assert "not live" in payload["disclaimer"]
    assert payload["source"] == "ARGUS static fixture"
    assert payload["observations"]
    assert all(item["freshness"] == "DEMO" for item in payload["observations"])
