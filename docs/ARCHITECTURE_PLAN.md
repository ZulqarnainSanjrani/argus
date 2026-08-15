# ARGUS Architecture Plan

## Approved direction

ARGUS is an independently designed modular product. OpenTerminalUI is not a dependency, foundation, template, or source of copied code/assets. It may be evaluated later only in a separately approved, bounded reference task. Maintained open-source libraries sit behind ARGUS-owned component and domain interfaces.

## Phase 1 topology

The browser application is a React/TypeScript single-page workstation built by Vite. Reusable visual semantics belong to `packages/design-system`; display-only financial conventions belong to `packages/financial-formatting`. FastAPI owns versioned HTTP contracts. `python/argus` is reserved for future provider-neutral domain code, while `db` is reserved for reviewed migrations.

```text
Browser → apps/web → ARGUS package interfaces
                    ↳ packages/design-system
                    ↳ packages/financial-formatting

Future HTTP boundary → apps/api (FastAPI) → fixture response only
```

No database, external provider, job runner, authentication, secret, AI model, or execution path exists in this phase. UI fixtures and API fixtures are intentionally separate so the shell remains usable while the API contract is evaluated.

## Next reviewed boundaries

Provider adapters, canonical observations, provenance storage, user identity, layout persistence, and deployments require separate decisions. Each should depend inward on ARGUS domain contracts rather than exposing provider-specific models to UI components.
