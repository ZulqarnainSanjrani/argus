# ARGUS

ARGUS is a desktop-first financial markets workstation with Pakistan fixed income as a specialist domain. This Phase 1 foundation deliberately uses conspicuously labelled, static **DEMO** fixtures; it has no live feeds, authentication, database connection, AI, or execution capability.

## Architecture

The npm workspace contains a Vite/React application and ARGUS-owned design-system and formatting packages. A separate FastAPI service exposes fixture-only public endpoints. Product code does not depend on OpenTerminalUI. See [`docs/ARCHITECTURE_PLAN.md`](docs/ARCHITECTURE_PLAN.md) and the ADRs in [`docs/ADRS`](docs/ADRS).

```text
apps/web                 React workstation shell
apps/api                 FastAPI application and Python configuration
packages/design-system   Shared visual primitives and tokens
packages/financial-formatting  Financial display semantics
python/argus             Future shared Python domain package boundary
db                       Future migrations/schema boundary (empty in Phase 1)
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

Alternatively, `docker compose up --build` starts both services for local development. The Compose file is not a production deployment definition.

## Quality commands

```bash
npm run lint
npm run typecheck
npm test
npm run build
pytest apps/api/tests
ruff check apps/api
```

## Phase 1 boundaries

All displayed observations are fictional fixtures for interaction validation, not market claims. No ingestion jobs, scheduled tasks, database migrations, credentials, or external provider setup exist yet. `db/`, `infra/`, `tests/`, and `python/argus/` establish ownership boundaries for later reviewed phases.

Report security issues privately to the maintainers. Contributions must preserve DEMO labelling, provenance semantics, accessibility, and the boundaries documented in the ADRs.
