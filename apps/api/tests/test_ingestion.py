from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from argus_api.db import Base
from argus_api.ingestion import TreasuryConnector, ingest
from argus_api.models import IngestionRun, Observation, RawArtifact
from argus_api.repository import validated_snapshot

FIXTURE = Path(__file__).parent / "fixtures" / "ust_synthetic.csv"


def setup():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_idempotent_ingestion_and_complete_provenance(tmp_path):
    engine = setup()
    connector = TreasuryConnector(2026)
    payload = FIXTURE.read_bytes()
    with Session(engine) as session:
        first = ingest(session, connector, payload, artifact_dir=str(tmp_path))
        second = ingest(session, connector, payload, artifact_dir=str(tmp_path))
        assert first["status"] == "VALID" and first["promoted"] == 13
        assert second["status"] == "DUPLICATE"
        assert session.scalar(select(func.count()).select_from(RawArtifact)) == 1
        row = validated_snapshot(session)[0]
        assert row["source"] == "U.S. Department of the Treasury daily par yield curve"
        assert row["source_format"] == "text/csv"
        assert row["parser_version"] == "ust-csv-1"
        assert row["raw_sha256"] == first["checksum"]
        assert row["market_status"] == "OFFICIAL_EOD"


def test_changed_payload_is_rejected_and_last_known_good_survives():
    engine = setup()
    connector = TreasuryConnector(2026)
    with Session(engine) as session:
        ingest(session, connector, FIXTURE.read_bytes())
        before = validated_snapshot(session)
        malformed = FIXTURE.read_bytes().replace(b"30 Yr", b"Mystery")
        result = ingest(session, connector, malformed)
        assert result["status"] == "REJECTED"
        assert validated_snapshot(session) == before
        assert session.scalars(select(IngestionRun).where(IngestionRun.status == "REJECTED")).one()


def test_out_of_range_validation_and_staleness():
    engine = setup()
    connector = TreasuryConnector(2026)
    with Session(engine) as session:
        rejected = FIXTURE.read_bytes().replace(b"1.13", b"31.00")
        assert ingest(session, connector, rejected)["status"] == "REJECTED"
        assert session.scalar(select(func.count()).select_from(Observation)) == 0
        old = datetime.now(UTC) - timedelta(days=4)
        assert (
            ingest(session, connector, FIXTURE.read_bytes(), retrieved_at=old)["status"] == "VALID"
        )
        assert {row["freshness"] for row in validated_snapshot(session)} == {"STALE"}
