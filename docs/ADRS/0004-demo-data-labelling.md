# ADR 0004: DEMO data labelling rule

- **Status:** Accepted
- **Date:** 2026-08-15

## Decision

Every fixture-bearing surface and response must identify its environment as `DEMO`. The shell carries a persistent disclaimer, affected panels disclose the static fixture source, and API responses include an environment, disclaimer, fixture source, and DEMO freshness on every observation.

## Rationale and consequences

Fictional values are useful for validating interaction and formatting but must never resemble factual, official, or live observations. `FACT` in a DEMO surface describes the intended future epistemic class, not the truth of the fixture. Production code must reject or isolate DEMO records before real ingestion is introduced.
