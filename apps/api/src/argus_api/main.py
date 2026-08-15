from datetime import UTC, datetime
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel


class Observation(BaseModel):
    symbol: str
    label: str
    value: float
    unit: Literal["percent", "index", "currency"]
    change: float
    change_unit: Literal["basis_points", "percent"]
    classification: Literal["FACT", "CALCULATED", "ARGUS VIEW"]
    freshness: Literal["DEMO"] = "DEMO"


class DemoSnapshot(BaseModel):
    environment: Literal["DEMO"] = "DEMO"
    disclaimer: str
    generated_at: datetime
    source: str
    observations: list[Observation]


app = FastAPI(
    title="ARGUS Public API",
    version="0.1.0",
    description="Phase 1 fixture-only API. Every market value is fictional DEMO data.",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": "DEMO", "external_calls": "disabled"}


@app.get("/api/v1/public/market-snapshot", response_model=DemoSnapshot, tags=["public"])
def market_snapshot() -> DemoSnapshot:
    return DemoSnapshot(
        disclaimer="Fictional fixture data; not live, official, or investment information.",
        generated_at=datetime(2026, 1, 15, 14, 30, tzinfo=UTC),
        source="ARGUS static fixture",
        observations=[
            Observation(symbol="DEMO-PK-POLICY", label="Policy rate", value=12.0, unit="percent", change=0.0, change_unit="basis_points", classification="FACT"),
            Observation(symbol="DEMO-PK-10Y", label="Pakistan 10Y", value=12.24, unit="percent", change=-1.3, change_unit="basis_points", classification="FACT"),
            Observation(symbol="DEMO-KSE100", label="KSE 100", value=78316.0, unit="index", change=-0.4, change_unit="percent", classification="FACT"),
        ],
    )
