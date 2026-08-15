import argparse

from .ingestion import REGISTRY, connector_for


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one bounded ARGUS ingestion manually")
    parser.add_argument("source", choices=sorted(REGISTRY))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    connector = connector_for(args.source)
    if not args.dry_run:
        connector.parse(connector.fetch())


if __name__ == "__main__":
    main()
