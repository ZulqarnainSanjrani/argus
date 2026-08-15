from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class CandidateObservation:
    series_id: str
    observation_date: date
    value: Decimal
    published_at: datetime | None = None


class ProviderConnector(Protocol):
    source_id: str

    def fetch(self) -> bytes: ...
    def parse(self, payload: bytes) -> list[CandidateObservation]: ...


@dataclass(frozen=True)
class SourceRegistration:
    source_id: str
    enabled: bool
    reason: str
    connector: ProviderConnector | None = None


REGISTRY = {
    "UST_DAILY_PAR_YIELD_CURVE": SourceRegistration(
        "UST_DAILY_PAR_YIELD_CURVE", False, "Live endpoint verification blocked by this environment"
    ),
    "SBP_POLICY_RATE": SourceRegistration(
        "SBP_POLICY_RATE", False, "Live endpoint and display-rights verification incomplete"
    ),
    "SBP_KIBOR": SourceRegistration(
        "SBP_KIBOR", False, "Live endpoint, format, and display-rights verification incomplete"
    ),
}


def connector_for(source_id: str) -> ProviderConnector:
    registration = REGISTRY[source_id]
    if not registration.enabled or registration.connector is None:
        raise RuntimeError(f"{source_id} disabled: {registration.reason}")
    return registration.connector
