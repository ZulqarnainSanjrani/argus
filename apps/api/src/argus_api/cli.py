import argparse

from .db import session_factory
from .ingestion import REGISTRY, connector_for, ingest


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one bounded ARGUS ingestion manually")
    parser.add_argument("source", choices=sorted(REGISTRY))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    connector = connector_for(args.source)
    payload = connector.fetch()
    if args.dry_run:
        print(f"VALID: {len(connector.parse(payload))} observations")
        return
    factory = session_factory()
    if factory is None:
        parser.error("ARGUS_DATABASE_URL is required")
    with factory() as session:
        print(ingest(session, connector, payload))


if __name__ == "__main__":
    main()
