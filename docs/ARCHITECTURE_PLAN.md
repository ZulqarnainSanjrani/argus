# ARGUS Architecture Plan

## Approved direction

ARGUS is an independently designed modular product. OpenTerminalUI is not a dependency, foundation, template, or source of copied code/assets. It may be evaluated later only in a separately approved, bounded reference task. Maintained open-source libraries sit behind ARGUS-owned component and domain interfaces.

## Phase 1 topology

The browser application is a React/TypeScript single-page workstation built by Vite. Reusable visual semantics belong to `packages/design-system`; display-only financial conventions belong to `packages/financial-formatting`. FastAPI owns versioned HTTP contracts. `python/argus` is reserved for future provider-neutral domain code, while `db` is reserved for reviewed migrations.

```text
Browser → apps/web → ARGUS package interfaces
                    ↳ packages/design-system
                    ↳ packages/financial-formatting

Browser → apps/api (FastAPI) → repository → PostgreSQL
                              ↳ manual provider-neutral ingestion boundary
```

PostgreSQL owns canonical immutable lineage and promoted last-known-good pointers. Alembic owns migrations. A manual CLI exists, but all publisher connectors fail closed pending live verification; there is no scheduler, browser-to-provider path, authentication, secret, AI model, or deployment in this slice. DEMO fixtures remain isolated fallback development data.

## Next reviewed boundaries

Provider adapters, canonical observations, provenance storage, user identity, layout persistence, and deployments require separate decisions. Each should depend inward on ARGUS domain contracts rather than exposing provider-specific models to UI components.
