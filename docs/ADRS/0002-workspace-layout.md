# ADR 0002: CSS Grid workspace foundation

- **Status:** Accepted
- **Date:** 2026-08-15

## Decision

Use semantic panels arranged by responsive CSS Grid for the Phase 1 shell. Preserve panel boundaries and controls so resizing, split views, serialization, and linked context can be introduced behind a dedicated workspace model.

## Rationale and consequences

This validates density and responsive behavior without prematurely selecting a docking framework or persisting unstable schemas. Phase 1 demonstrates split-capable composition but does not claim drag/drop, resizing, or persistence are complete.
