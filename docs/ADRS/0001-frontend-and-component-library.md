# ADR 0001: React, Vite, and ARGUS-owned components

- **Status:** Accepted
- **Date:** 2026-08-15

## Decision

Use TypeScript, React, and Vite. Build semantic workstation primitives in `packages/design-system` using CSS tokens and accessible HTML. Use Recharts only behind the application chart panel boundary.

## Rationale and consequences

React has a maintained ecosystem and supports modular interactive panels; Vite provides a small development/build surface. An ARGUS-owned component layer prevents template-driven visual inconsistency and makes chart libraries replaceable. Phase 1 accepts that a more capable table/chart engine may be evaluated later.
