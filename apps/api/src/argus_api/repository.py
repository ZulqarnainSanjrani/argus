from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import DataSource, Observation, ObservationVintage, SeriesDefinition, ValidationStatus


def validated_snapshot(session: Session) -> list[dict]:
    """Return only promoted VALID vintages; rejected runs can never displace them."""
    statement = (
        select(Observation, ObservationVintage, SeriesDefinition, DataSource)
        .join(ObservationVintage, ObservationVintage.id == Observation.active_vintage_id)
        .join(SeriesDefinition, SeriesDefinition.id == Observation.series_id)
        .join(DataSource, DataSource.id == SeriesDefinition.source_id)
        .where(ObservationVintage.validation_status == ValidationStatus.VALID)
        .order_by(SeriesDefinition.id)
    )
    now = datetime.now(UTC)
    rows = []
    for observation, vintage, series, source in session.execute(statement):
        retrieved_at = vintage.retrieved_at
        if retrieved_at.tzinfo is None:  # SQLite migration tests do not preserve tzinfo.
            retrieved_at = retrieved_at.replace(tzinfo=UTC)
        age = max(0, int((now - retrieved_at).total_seconds()))
        rows.append(
            {
                "symbol": series.id,
                "label": series.label,
                "value": float(vintage.value),
                "unit": series.unit,
                "classification": series.classification,
                "freshness": "STALE" if age > series.stale_after_seconds else "FRESH",
                "observation_time": observation.observation_time,
                "observation_date": observation.observation_date,
                "retrieved_at": vintage.retrieved_at,
                "validation_status": vintage.validation_status.value,
                "source": source.publisher,
                "source_url": vintage.source_url,
            }
        )
    return rows
