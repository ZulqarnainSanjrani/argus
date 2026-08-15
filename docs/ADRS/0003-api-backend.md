# ADR 0003: FastAPI backend

- **Status:** Accepted
- **Date:** 2026-08-15

## Decision

Use Python 3.12 and FastAPI for versioned API endpoints, typed response models, and generated OpenAPI documentation. Keep routes thin and reserve `python/argus` for future domain logic.

## Rationale and consequences

Python fits future financial and ingestion work while FastAPI provides explicit schemas and straightforward testing. The current API performs no I/O and returns only deterministic fixtures.
