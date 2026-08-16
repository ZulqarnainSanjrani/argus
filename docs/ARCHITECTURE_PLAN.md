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

PostgreSQL owns canonical immutable lineage and promoted last-known-good pointers.
Alembic owns migrations. A manual CLI exposes the merged official U.S. Treasury
EOD CSV connector; it has no scheduler and is not a live feed. SBP policy rate
fails closed because its structured official route requires credentials, its
public pages do not provide a current effective-dated observation contract, and
redistribution rights remain unverified. There is no browser-to-provider path,
authentication, secret, AI model, or deployment in this slice. DEMO fixtures
remain isolated fallback development data.

## Static workstation foundation status

The Phase 1 browser shell is implemented as an ARGUS-owned, desktop-first
workspace. It consumes only `GET /api/v1/demo/home` for its synthetic home
fixture and renders loading, empty, stale, and connection-error boundaries. The
home composition includes Pakistan rates and curve surfaces, a cross-asset
strip, an events calendar, and local source-health status. All fixture-bearing
surfaces retain persistent `DEMO` labelling; calculated curve output and
illustrative ARGUS commentary have separate classifications.

The demo endpoint performs no external I/O. Its CORS allow-list is limited to
the local Vite development origins. Authentication, live market data, provider
calls, ingestion scheduling, AI calls, and layout persistence remain outside
this bounded milestone.

The workstation UI was manually verified at 1920×1080 and 1440×1080. Generated
screenshot artifacts are intentionally excluded from version control.

## Next reviewed boundaries

Additional provider adapters, user identity, layout persistence, and deployments
require separate decisions. The merged Treasury slice establishes canonical
observations and provenance storage; future providers should depend inward on
those ARGUS domain contracts rather than expose provider-specific models to UI
components.
