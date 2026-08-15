from datetime import UTC, date, datetime
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from .db import session_factory
from .repository import validated_snapshot


class SnapshotObservation(BaseModel):
    symbol: str
    label: str
    value: float | None
    unit: str
    classification: Literal["FACT", "CALCULATED", "ARGUS VIEW"]
    freshness: Literal[
        "FRESH", "DELAYED", "STALE", "PARSING_ERROR", "SOURCE_UNAVAILABLE", "DEMO", "N/A"
    ]
    observation_date: date | None = None
    observation_time: datetime | None = None
    retrieved_at: datetime | None = None
    validation_status: str
    source: str
    source_url: str | None = None


class Snapshot(BaseModel):
    environment: Literal["DATA", "DEMO"]
    disclaimer: str
    generated_at: datetime
    observations: list[SnapshotObservation]


app = FastAPI(title="ARGUS Public API", version="0.2.0")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "database": "configured" if session_factory() else "not_configured",
        "automatic_jobs": "disabled",
    }


@app.get("/api/v1/public/market-snapshot", response_model=Snapshot, tags=["public"])
def market_snapshot() -> Snapshot:
    factory = session_factory()
    observations = []
    if factory:
        with factory() as session:
            observations = validated_snapshot(session)
    if observations:
        return Snapshot(
            environment="DATA",
            disclaimer="Validated official observations; inspect provenance and freshness.",
            generated_at=datetime.now(UTC),
            observations=observations,
        )
    return Snapshot(
        environment="DEMO",
        disclaimer="Fictional local-development fixtures; not live, official, or investment information.",
        generated_at=datetime.now(UTC),
        observations=[
            SnapshotObservation(
                symbol="DEMO-PK-POLICY",
                label="Policy rate",
                value=12.0,
                unit="percent",
                classification="FACT",
                freshness="DEMO",
                validation_status="DEMO_ONLY",
                source="ARGUS synthetic fixture",
            )
        ],
    )
