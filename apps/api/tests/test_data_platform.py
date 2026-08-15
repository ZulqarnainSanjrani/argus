from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from argus_api.db import Base
from argus_api.ingestion import connector_for
from argus_api.models import (
    DataSource,
    IngestionRun,
    Observation,
    ObservationVintage,
    RawArtifact,
    SeriesDefinition,
    SourceFetch,
    ValidationStatus,
)
from argus_api.repository import validated_snapshot


def seed(session: Session):
    now = datetime.now(UTC)
    source = DataSource(
        id="TEST",
        publisher="Official Test Publisher",
        canonical_url="https://example.test/data",
        rights_url="https://example.test/rights",
        enabled=True,
        restrictions="test only",
    )
    fetch = SourceFetch(
        source_id="TEST",
        requested_url=source.canonical_url,
        retrieved_at=now,
        status_code=200,
        error_code=None,
    )
    session.add_all([source, fetch])
    session.flush()
    artifact = RawArtifact(
        fetch_id=fetch.id,
        sha256="a" * 64,
        media_type="text/csv",
        byte_length=10,
        storage_reference=None,
    )
    run = IngestionRun(
        source_id="TEST",
        fetch_id=fetch.id,
        parser_version="test-1",
        started_at=now,
        finished_at=now,
        status="VALID",
    )
    series = SeriesDefinition(
        id="TEST.RATE",
        source_id="TEST",
        label="Test rate",
        unit="percent",
        classification="FACT",
        stale_after_seconds=3600,
    )
    session.add_all([artifact, run, series])
    session.flush()
    observation = Observation(
        series_id=series.id, observation_date=datetime.now(UTC).date(), observation_time=None
    )
    session.add(observation)
    session.flush()
    good = ObservationVintage(
        observation_id=observation.id,
        run_id=run.id,
        artifact_id=artifact.id,
        vintage_number=1,
        value=Decimal("4.25"),
        retrieved_at=now,
        validation_status=ValidationStatus.VALID,
        source_url=source.canonical_url,
        raw_sha256=artifact.sha256,
    )
    session.add(good)
    session.flush()
    observation.active_vintage_id = good.id
    session.commit()
    return observation, run, artifact


def test_migration_schema_and_last_known_good():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    assert len(Base.metadata.tables) == 8
    with Session(engine) as session:
        observation, run, artifact = seed(session)
        session.add(
            ObservationVintage(
                observation_id=observation.id,
                run_id=run.id,
                artifact_id=artifact.id,
                vintage_number=2,
                value=Decimal(99),
                retrieved_at=datetime.now(UTC),
                validation_status=ValidationStatus.REJECTED,
                source_url="https://example.test/data",
                raw_sha256="b" * 64,
            )
        )
        session.commit()
        rows = validated_snapshot(session)
        assert rows[0]["value"] == 4.25
        assert rows[0]["validation_status"] == "VALID"


def test_unverified_sources_are_disabled():
    for source in ("UST_DAILY_PAR_YIELD_CURVE", "SBP_POLICY_RATE", "SBP_KIBOR"):
        try:
            connector_for(source)
        except RuntimeError as error:
            assert "disabled" in str(error)
        else:
            raise AssertionError("unverified connector enabled")
