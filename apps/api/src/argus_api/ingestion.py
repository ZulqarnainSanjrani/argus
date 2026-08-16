"""Bounded provider adapters and atomic last-known-good ingestion."""

from __future__ import annotations

import csv
import hashlib
import io
import os
import urllib.request
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    DataSource,
    IngestionRun,
    Observation,
    ObservationVintage,
    RawArtifact,
    SeriesDefinition,
    SourceFetch,
    ValidationResult,
    ValidationStatus,
)

PARSER_VERSION = "ust-csv-1"
UST_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&"
    "field_tdr_date_value={year}&page&_format=csv"
)
UST_POLICY = "https://home.treasury.gov/about/general-information/website-policies-notices"
SBP_URL = "https://www.sbp.org.pk/our-operations/monetary-policy"
TENORS = {
    "1 Mo": "1M",
    "1.5 Month": "1.5M",
    "2 Mo": "2M",
    "3 Mo": "3M",
    "4 Mo": "4M",
    "6 Mo": "6M",
    "1 Yr": "1Y",
    "2 Yr": "2Y",
    "3 Yr": "3Y",
    "5 Yr": "5Y",
    "7 Yr": "7Y",
    "10 Yr": "10Y",
    "20 Yr": "20Y",
    "30 Yr": "30Y",
}


class PayloadError(ValueError):
    """The publisher payload cannot be safely promoted."""


@dataclass(frozen=True)
class CandidateObservation:
    series_id: str
    observation_date: date
    value: Decimal
    published_at: datetime | None = None


class ProviderConnector(Protocol):
    source_id: str
    source_url: str
    source_format: str
    parser_version: str

    def fetch(self) -> bytes: ...
    def parse(self, payload: bytes) -> list[CandidateObservation]: ...


class TreasuryConnector:
    source_id = "UST_DAILY_PAR_YIELD_CURVE"
    source_format = "text/csv"
    parser_version = PARSER_VERSION

    def __init__(self, year: int | None = None):
        self.year = year or datetime.now(UTC).year
        self.source_url = UST_URL.format(year=self.year)

    def fetch(self) -> bytes:
        request = urllib.request.Request(
            self.source_url,
            headers={
                "Accept": "text/csv",
                "User-Agent": os.getenv("ARGUS_USER_AGENT", "ARGUS/0.2"),
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200 or "csv" not in response.headers.get_content_type():
                raise PayloadError("Treasury response was not a CSV success response")
            return response.read(5_000_001)

    def parse(self, payload: bytes) -> list[CandidateObservation]:
        if not payload or len(payload) > 5_000_000 or payload.lstrip().startswith(b"<"):
            raise PayloadError("payload is empty, oversized, or HTML/XML")
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise PayloadError("payload is not UTF-8 CSV") from error
        reader = csv.DictReader(io.StringIO(text))
        headers = reader.fieldnames or []
        unknown = set(headers) - ({"Date"} | set(TENORS))
        if "Date" not in headers or unknown or len(set(headers)) != len(headers):
            raise PayloadError(f"changed CSV schema: unknown={sorted(unknown)}")
        results: list[CandidateObservation] = []
        seen: set[date] = set()
        for row in reader:
            try:
                observed = (
                    datetime.strptime(row["Date"].strip(), "%m/%d/%Y")
                    .replace(tzinfo=UTC)
                    .date()
                )
            except (ValueError, AttributeError) as error:
                raise PayloadError("invalid observation date") from error
            if observed in seen:
                raise PayloadError("duplicate observation date")
            seen.add(observed)
            day: list[CandidateObservation] = []
            for column, tenor in TENORS.items():
                raw = row.get(column, "").strip()
                if not raw:  # Treasury legitimately added maturities over time.
                    continue
                try:
                    value = Decimal(raw)
                except InvalidOperation as error:
                    raise PayloadError(f"non-numeric {column}") from error
                if not Decimal(0) < value < Decimal(30):
                    raise PayloadError(f"out-of-range {column}")
                day.append(CandidateObservation(f"US.UST.PAR_YIELD.{tenor}", observed, value))
            if len(day) < 6:
                raise PayloadError("partial curve has fewer than six tenors")
            results.extend(day)
        if not results:
            raise PayloadError("CSV has no observations")
        return results


@dataclass(frozen=True)
class SourceRegistration:
    source_id: str
    name: str
    canonical_url: str
    source_format: str
    mode: str
    reason: str
    connector_factory: type[TreasuryConnector] | None = None


REGISTRY = {
    "UST_DAILY_PAR_YIELD_CURVE": SourceRegistration(
        "UST_DAILY_PAR_YIELD_CURVE",
        "U.S. Department of the Treasury daily par yield curve",
        UST_URL,
        "text/csv",
        "OFFICIAL_EOD",
        "Official machine-readable annual CSV",
        TreasuryConnector,
    ),
    "SBP_POLICY_RATE": SourceRegistration(
        "SBP_POLICY_RATE",
        "State Bank of Pakistan policy rate",
        SBP_URL,
        "text/html",
        "FIXTURE_ONLY",
        (
            "EasyData API requires account/API key; credential-free pages lack a current "
            "effective-dated observation contract and explicit storage/public-redistribution "
            "permission; live adapter disabled"
        ),
    ),
}


def connector_for(source_id: str) -> ProviderConnector:
    registration = REGISTRY[source_id]
    if registration.connector_factory is None:
        raise RuntimeError(f"{source_id} disabled: {registration.reason}")
    return registration.connector_factory()


def ingest(
    session: Session,
    connector: ProviderConnector,
    payload: bytes | None = None,
    retrieved_at: datetime | None = None,
    artifact_dir: str | None = None,
) -> dict[str, int | str]:
    """Ingest one payload atomically; failures are audited and never promoted."""
    now = retrieved_at or datetime.now(UTC)
    source = session.get(DataSource, connector.source_id)
    if source is None:
        source = DataSource(
            id=connector.source_id,
            publisher=REGISTRY[connector.source_id].name,
            canonical_url=connector.source_url,
            rights_url=UST_POLICY,
            enabled=True,
            restrictions="OFFICIAL / EOD; not live",
            source_format=connector.source_format,
        )
        session.add(source)
    fetch = SourceFetch(
        source_id=connector.source_id,
        requested_url=connector.source_url,
        retrieved_at=now,
        status_code=200,
        error_code=None,
    )
    session.add(fetch)
    session.flush()
    raw = payload if payload is not None else connector.fetch()
    digest = hashlib.sha256(raw).hexdigest()
    existing = session.scalar(select(RawArtifact).where(RawArtifact.sha256 == digest))
    if existing:
        session.rollback()
        return {"status": "DUPLICATE", "promoted": 0, "checksum": digest}
    storage_reference = None
    root = artifact_dir or os.getenv("ARGUS_ARTIFACT_DIR")
    if root:
        path = Path(root) / connector.source_id / f"{digest}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        storage_reference = str(path)
    artifact = RawArtifact(
        fetch_id=fetch.id,
        sha256=digest,
        media_type=connector.source_format,
        byte_length=len(raw),
        storage_reference=storage_reference,
    )
    run = IngestionRun(
        source_id=connector.source_id,
        fetch_id=fetch.id,
        parser_version=connector.parser_version,
        started_at=now,
        finished_at=None,
        status="RUNNING",
    )
    session.add_all([artifact, run])
    session.flush()
    try:
        candidates = connector.parse(raw)
    except PayloadError as error:
        run.status = "REJECTED"
        run.finished_at = now
        session.add(
            ValidationResult(
                run_id=run.id,
                status=ValidationStatus.REJECTED,
                rule_code="PAYLOAD_INVALID",
                detail=str(error),
            )
        )
        session.commit()
        return {"status": "REJECTED", "promoted": 0, "checksum": digest}
    promoted = 0
    for candidate in candidates:
        series = session.get(SeriesDefinition, candidate.series_id)
        if series is None:
            tenor = candidate.series_id.rsplit(".", 1)[-1]
            series = SeriesDefinition(
                id=candidate.series_id,
                source_id=connector.source_id,
                label=f"U.S. Treasury {tenor} par yield",
                unit="PERCENT_PER_ANNUM",
                classification="FACT",
                stale_after_seconds=259200,
            )
            session.add(series)
            session.flush()
        observation = session.scalar(
            select(Observation).where(
                Observation.series_id == candidate.series_id,
                Observation.observation_date == candidate.observation_date,
            )
        )
        if observation is None:
            observation = Observation(
                series_id=candidate.series_id,
                observation_date=candidate.observation_date,
                observation_time=None,
            )
            session.add(observation)
            session.flush()
        vintage_number = len(observation.vintages) + 1
        vintage = ObservationVintage(
            observation_id=observation.id,
            run_id=run.id,
            artifact_id=artifact.id,
            vintage_number=vintage_number,
            value=candidate.value,
            published_at=candidate.published_at,
            retrieved_at=now,
            validation_status=ValidationStatus.VALID,
            source_url=connector.source_url,
            raw_sha256=digest,
        )
        session.add(vintage)
        session.flush()
        observation.active_vintage_id = vintage.id
        promoted += 1
    run.status = "VALID"
    run.finished_at = now
    session.add(
        ValidationResult(
            run_id=run.id,
            status=ValidationStatus.VALID,
            rule_code="CURVE_COMPLETE",
            detail=f"Promoted {promoted} validated observations",
        )
    )
    session.commit()
    return {"status": "VALID", "promoted": promoted, "checksum": digest}
