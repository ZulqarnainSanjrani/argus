import os
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from argus_api.main import app
from argus_api.models import ObservationVintage, ValidationStatus
from argus_api.repository import validated_snapshot
from test_data_platform import seed

EXPECTED_TABLES = {
    "alembic_version",
    "data_sources",
    "ingestion_runs",
    "observation_vintages",
    "observations",
    "raw_artifacts",
    "series_definitions",
    "source_fetches",
    "validation_results",
}


@pytest.fixture()
def postgres_engine():
    url = os.getenv("ARGUS_TEST_DATABASE_URL")
    if not url:
        pytest.skip("ARGUS_TEST_DATABASE_URL is required for PostgreSQL integration tests")
    engine = create_engine(url, pool_pre_ping=True)
    table_names = EXPECTED_TABLES - {"alembic_version"}
    with engine.begin() as connection:
        quoted = ", ".join(f'"{name}"' for name in sorted(table_names))
        connection.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"))
    yield engine
    engine.dispose()


def test_canonical_schema_was_migrated_to_postgresql(postgres_engine):
    assert EXPECTED_TABLES <= set(inspect(postgres_engine).get_table_names())
    assert postgres_engine.dialect.name == "postgresql"


def test_postgresql_preserves_last_known_good_active_vintage(postgres_engine):
    with Session(postgres_engine) as session:
        observation, run, artifact = seed(session)
        session.add(
            ObservationVintage(
                observation_id=observation.id,
                run_id=run.id,
                artifact_id=artifact.id,
                vintage_number=2,
                value=Decimal("99"),
                retrieved_at=datetime.now(UTC),
                validation_status=ValidationStatus.REJECTED,
                source_url="https://example.test/rejected",
                raw_sha256="b" * 64,
            )
        )
        session.commit()
        rows = validated_snapshot(session)
        assert [(row["symbol"], row["value"]) for row in rows] == [("TEST.RATE", 4.25)]


def test_snapshot_remains_demo_with_empty_postgresql_database(postgres_engine, monkeypatch):
    monkeypatch.setenv("ARGUS_DATABASE_URL", str(postgres_engine.url))
    response = TestClient(app).get("/api/v1/public/market-snapshot")
    assert response.status_code == 200
    payload = response.json()
    assert payload["environment"] == "DEMO"
    assert payload["observations"][0]["validation_status"] == "DEMO_ONLY"
    assert payload["observations"][0]["source"] == "ARGUS synthetic fixture"
