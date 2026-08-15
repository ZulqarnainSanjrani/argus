from datetime import UTC, date, datetime
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .db import session_factory
from .repository import validated_snapshot
from .ingestion import REGISTRY


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
    published_at: datetime | None = None
    parser_version: str | None = None
    raw_sha256: str | None = None
    source_format: str | None = None
    market_status: Literal["OFFICIAL_EOD"] | None = None


class Snapshot(BaseModel):
    environment: Literal["DATA", "DEMO"]
    disclaimer: str
    generated_at: datetime
    observations: list[SnapshotObservation]


class DemoRate(BaseModel):
    instrument: str
    tenor: str
    yield_percent: float
    move_bp: float
    previous_yield_percent: float


class DemoMarketItem(BaseModel):
    symbol: str
    label: str
    value: float
    display: str
    move: float
    move_unit: Literal["percent", "bp", "flat"]


class DemoEvent(BaseModel):
    time: str
    region: str
    event: str
    importance: Literal["HIGH", "MEDIUM", "LOW"]


class DemoSourceHealth(BaseModel):
    source: str
    status: Literal["READY", "STALE", "DISABLED", "ERROR"]
    detail: str


class DemoHome(BaseModel):
    environment: Literal["DEMO"]
    disclaimer: str
    fixture_source: str
    generated_at: datetime
    stale_after_seconds: int
    rates: list[DemoRate]
    global_markets: list[DemoMarketItem]
    events: list[DemoEvent]
    source_health: list[DemoSourceHealth]


app = FastAPI(title="ARGUS Public API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "database": "configured" if session_factory() else "not_configured",
        "automatic_jobs": "disabled",
    }


@app.get("/api/v1/public/sources", tags=["public"])
def sources() -> list[dict[str, str]]:
    """Expose the bounded source registry, including disabled fixture-only entries."""
    return [
        {
            "source_id": item.source_id,
            "name": item.name,
            "canonical_url": item.canonical_url,
            "source_format": item.source_format,
            "mode": item.mode,
            "reason": item.reason,
        }
        for item in REGISTRY.values()
    ]


@app.get("/api/v1/demo/home", response_model=DemoHome, tags=["demo"])
def demo_home() -> DemoHome:
    """Return deterministic, conspicuously labelled fixtures for the Phase 1 shell."""
    return DemoHome(
        environment="DEMO",
        disclaimer=("Fictional interface fixtures; not live, official, or investment information."),
        fixture_source="ARGUS synthetic Phase 1 fixture",
        generated_at=datetime.now(UTC),
        stale_after_seconds=300,
        rates=[
            DemoRate(
                instrument="3M MTB",
                tenor="3M",
                yield_percent=11.82,
                move_bp=-3.2,
                previous_yield_percent=11.85,
            ),
            DemoRate(
                instrument="6M MTB",
                tenor="6M",
                yield_percent=11.74,
                move_bp=-2.1,
                previous_yield_percent=11.76,
            ),
            DemoRate(
                instrument="12M MTB",
                tenor="1Y",
                yield_percent=11.55,
                move_bp=-4.8,
                previous_yield_percent=11.60,
            ),
            DemoRate(
                instrument="3Y PIB",
                tenor="3Y",
                yield_percent=11.69,
                move_bp=1.5,
                previous_yield_percent=11.68,
            ),
            DemoRate(
                instrument="5Y PIB",
                tenor="5Y",
                yield_percent=11.91,
                move_bp=2.7,
                previous_yield_percent=11.88,
            ),
            DemoRate(
                instrument="10Y PIB",
                tenor="10Y",
                yield_percent=12.24,
                move_bp=-1.3,
                previous_yield_percent=12.25,
            ),
        ],
        global_markets=[
            DemoMarketItem(
                symbol="SPX",
                label="S&P 500",
                value=5412.18,
                display="5,412.18",
                move=0.42,
                move_unit="percent",
            ),
            DemoMarketItem(
                symbol="US10Y",
                label="US 10Y",
                value=4.21,
                display="4.21%",
                move=-4.0,
                move_unit="bp",
            ),
            DemoMarketItem(
                symbol="DXY",
                label="DXY",
                value=103.84,
                display="103.84",
                move=-0.18,
                move_unit="percent",
            ),
            DemoMarketItem(
                symbol="BRENT",
                label="Brent",
                value=82.14,
                display="82.14",
                move=0.76,
                move_unit="percent",
            ),
            DemoMarketItem(
                symbol="GOLD",
                label="Gold",
                value=2326.40,
                display="2,326.40",
                move=0.31,
                move_unit="percent",
            ),
            DemoMarketItem(
                symbol="USDPKR",
                label="USD / PKR",
                value=278.35,
                display="278.35",
                move=0,
                move_unit="flat",
            ),
        ],
        events=[
            DemoEvent(
                time="09:00 PKT",
                region="PK",
                event="T-bill auction result window",
                importance="HIGH",
            ),
            DemoEvent(
                time="12:00 PKT",
                region="PK",
                event="Weekly FX reserves fixture",
                importance="MEDIUM",
            ),
            DemoEvent(
                time="13:30 UTC", region="US", event="Initial claims fixture", importance="MEDIUM"
            ),
            DemoEvent(
                time="14:00 UTC", region="US", event="Existing home sales fixture", importance="LOW"
            ),
        ],
        source_health=[
            DemoSourceHealth(
                source="Pakistan rates fixture", status="READY", detail="Static · local"
            ),
            DemoSourceHealth(
                source="Global markets fixture", status="READY", detail="Static · local"
            ),
            DemoSourceHealth(source="Events fixture", status="READY", detail="Static · local"),
            DemoSourceHealth(
                source="External providers",
                status="DISABLED",
                detail="No connectors in this milestone",
            ),
        ],
    )


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
