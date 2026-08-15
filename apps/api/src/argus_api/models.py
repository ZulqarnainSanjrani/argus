import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class ValidationStatus(str, enum.Enum):
    VALID = "VALID"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    publisher: Mapped[str] = mapped_column(String(200))
    canonical_url: Mapped[str] = mapped_column(Text)
    rights_url: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    restrictions: Mapped[str] = mapped_column(Text, default="")
    source_format: Mapped[str] = mapped_column(String(80), default="unknown")


class SourceFetch(Base):
    __tablename__ = "source_fetches"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[str] = mapped_column(ForeignKey("data_sources.id"))
    requested_url: Mapped[str] = mapped_column(Text)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status_code: Mapped[int | None]
    error_code: Mapped[str | None] = mapped_column(String(80))


class RawArtifact(Base):
    __tablename__ = "raw_artifacts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    fetch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_fetches.id"), unique=True)
    sha256: Mapped[str] = mapped_column(String(64), unique=True)
    media_type: Mapped[str] = mapped_column(String(150))
    byte_length: Mapped[int]
    storage_reference: Mapped[str | None] = mapped_column(Text)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[str] = mapped_column(ForeignKey("data_sources.id"))
    fetch_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("source_fetches.id"))
    parser_version: Mapped[str] = mapped_column(String(80))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30))


class ValidationResult(Base):
    __tablename__ = "validation_results"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id"))
    status: Mapped[ValidationStatus] = mapped_column(Enum(ValidationStatus))
    rule_code: Mapped[str] = mapped_column(String(100))
    detail: Mapped[str] = mapped_column(Text)


class SeriesDefinition(Base):
    __tablename__ = "series_definitions"
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("data_sources.id"))
    label: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str] = mapped_column(String(60))
    classification: Mapped[str] = mapped_column(String(30), default="FACT")
    stale_after_seconds: Mapped[int]


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (UniqueConstraint("series_id", "observation_date"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    series_id: Mapped[str] = mapped_column(ForeignKey("series_definitions.id"))
    observation_date: Mapped[date] = mapped_column(Date)
    observation_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    active_vintage_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    vintages: Mapped[list["ObservationVintage"]] = relationship(
        back_populates="observation", foreign_keys="ObservationVintage.observation_id"
    )


class ObservationVintage(Base):
    __tablename__ = "observation_vintages"
    __table_args__ = (UniqueConstraint("observation_id", "vintage_number"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    observation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("observations.id"))
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_runs.id"))
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("raw_artifacts.id"))
    vintage_number: Mapped[int]
    value: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    validation_status: Mapped[ValidationStatus] = mapped_column(Enum(ValidationStatus))
    source_url: Mapped[str] = mapped_column(Text)
    raw_sha256: Mapped[str] = mapped_column(String(64))
    observation: Mapped[Observation] = relationship(
        back_populates="vintages", foreign_keys=[observation_id]
    )
