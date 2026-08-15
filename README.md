# ARGUS

ARGUS is a desktop-first financial markets workstation with Pakistan fixed income as a specialist domain. The first real-data slice adds a bounded official U.S. Treasury daily par-yield CSV adapter, PostgreSQL persistence, validation/quarantine, immutable provenance, and last-known-good publication. The SBP policy-rate adapter remains fixture-only because no stable machine-readable route and sufficiently clear redistribution permission were verified. Conspicuously labelled **DEMO** fixtures remain only where no validated database observation exists.

## Architecture

The npm workspace contains a Vite/React application and ARGUS-owned design-system and formatting packages. A separate FastAPI service exposes fixture-only public endpoints. Product code does not depend on OpenTerminalUI. See [`docs/ARCHITECTURE_PLAN.md`](docs/ARCHITECTURE_PLAN.md) and the ADRs in [`docs/ADRS`](docs/ADRS).

```text
apps/web                 React workstation shell
apps/api                 FastAPI API, canonical models, registry, and manual CLI
packages/design-system   Shared visual primitives and tokens
packages/financial-formatting  Financial display semantics
python/argus             Future shared Python domain package boundary
db                       Alembic migration and PostgreSQL schema boundary
tests                    Cross-application test boundary
docs/ADRS                Architecture decisions
infra                    Local-development infrastructure
```

## Prerequisites and setup

- Node.js 20+
- Python 3.12+
- Docker and Docker Compose (optional)

```bash
cp .env.example .env
npm install
python -m venv .venv
. .venv/bin/activate
pip install -e 'apps/api[dev]'
```

No secret values are needed. Start the web application with `npm run dev:web`; start the API with `uvicorn argus_api.main:app --app-dir apps/api --reload`. OpenAPI is available at `http://localhost:8000/docs`.

Alternatively, `docker compose up --build` starts PostgreSQL, the API, and web application for local development. Run `alembic -c db/alembic.ini upgrade head` before the first API request. The Compose file is not a production deployment definition. See the [manual ingestion runbook](docs/INGESTION_RUNBOOK.md).

## Quality commands

```bash
npm run lint
npm run typecheck
npm test
npm run build
pytest apps/api/tests
ruff check apps/api
```

## Data-platform boundaries

The snapshot API reads promoted, validated database vintages when they exist and otherwise returns an explicitly `DEMO`-classified local fixture. No automatic jobs, credentials, or browser-to-provider calls exist. Treasury data is always labelled `OFFICIAL_EOD`, never live. Official values carry publisher, source URL, observation/publication/retrieval times, format, parser version, validation, checksum, classification, and freshness.

Report security issues privately to the maintainers. Contributions must preserve DEMO labelling, provenance semantics, accessibility, and the boundaries documented in the ADRs.
