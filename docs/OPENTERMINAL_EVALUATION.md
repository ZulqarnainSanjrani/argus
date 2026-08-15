# OpenTerminalUI evaluation for ARGUS

**Decision date:** 2026-08-15

**Project evaluated:** [Hitheshkaranth/OpenTerminalUI](https://github.com/Hitheshkaranth/OpenTerminalUI), default branch `main`, latest inspected commit [`fc16fd64`](https://github.com/Hitheshkaranth/OpenTerminalUI/commit/fc16fd646405aec7a5525387be89c0cb376137c5) (2026-07-11)

**Scope:** public repository and direct dependency/provider/deployment documentation only. No OpenTerminalUI source was copied into ARGUS, no dependencies were installed, and neither application was run.

## Executive decision

**Final recommendation: use OpenTerminalUI selectively as component/code reference. Do not adopt it as the ARGUS foundation.**

OpenTerminalUI is a young, ambitious MIT-licensed self-hosted workstation with useful examples of a terminal shell, keyboard navigation, linked charts, screeners, portfolio/risk tools, backtesting, alerts, saved views, and provider adapters. Those are valuable references for bounded implementation ideas. Its current shape is nevertheless a poor foundation for ARGUS: it is a very broad single-maintainer application, its Python dependencies are unpinned, its data/provider assumptions are oriented principally to US and Indian trading, its authentication has a critical public-product password-reset defect, and its combined long-running FastAPI/Redis/database/ML design does not fit a durable zero-fixed-cost public deployment.

ARGUS would have to replace or substantially redesign the identity boundary, tenancy model, provenance-first data layer, ingestion system, official Pakistan adapters, deployment topology, public quotas, and much of the information architecture. At that point adopting the repository buys less than selecting a few well-maintained components behind clean ARGUS interfaces.

## Method and evidence labels

This review distinguishes:

- **VERIFIED** — directly supported by a linked primary source inspected on 2026-08-15. Repository statements establish what the project contains or claims, not that every feature is correct in production.
- **INFERENCE** — an engineering conclusion drawn from one or more verified facts. It must be validated with a focused spike before adoption.
- **NOT VERIFIED** — the public evidence was insufficient; no favorable assumption is made.

Repository evidence is pinned to the inspected commit wherever practical. Provider and platform pages are live documents and therefore include an explicit access date. The supplied `docs/ARGUS_PRODUCT_SPEC.md` was reviewed before this evaluation. The requested `docs/ARCHITECTURE_PLAN.md` was not present in the task checkout or the public ARGUS `main` tree as of 2026-08-15; this report therefore does not invent its contents. The comparison baseline is the product spec's clean, modular, provider-independent, multi-user, provenance-first, zero-fixed-cost direction.

## 1. Repository, license, and maintenance

| Topic | Verified facts | Assessment / inference |
|---|---|---|
| Ownership and age | **VERIFIED:** GitHub reports creation on 2026-02-13, a single listed contributor, and an unarchived repository. The [contributors endpoint](https://api.github.com/repos/Hitheshkaranth/OpenTerminalUI/contributors) attributed all listed contributions to one account when checked. The [repository API](https://api.github.com/repos/Hitheshkaranth/OpenTerminalUI) reported 107 stars, 26 forks, and no open issues on 2026-08-15. | **INFERENCE:** bus factor is one. Stars and feature count are not evidence of production maturity, independent review, or sustained maintenance. |
| Activity | **VERIFIED:** the latest inspected commit was 2026-07-11; releases `v0.3.0` through `v0.6.0` were published between 2026-05-17 and 2026-07-05 in the [release record](https://github.com/Hitheshkaranth/OpenTerminalUI/releases). The repository was about six months old at review. | **INFERENCE:** recent, rapid activity is positive, but the short history and high change velocity increase upgrade and regression risk. The anomalous earlier `v1.0.0` followed by `v0.x` releases weakens confidence in semantic-versioning discipline. |
| License | **VERIFIED:** the root [MIT license](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/LICENSE) permits use, modification, distribution, sublicensing, and sale with preservation of copyright/license notices and an “as is” disclaimer. | The repository license is compatible with selective reuse. It does **not** grant rights to third-party market data, model weights, news, trademarks, screenshots, or provider services. Any reused file would need provenance and notice review. |
| Releases and support | **VERIFIED:** six GitHub releases were visible, but the [repository tree](https://github.com/Hitheshkaranth/OpenTerminalUI/tree/fc16fd646405aec7a5525387be89c0cb376137c5) had no published architecture/security/data-rights documentation matching the README's described `docs/` wiki. Two visible historical issues were pull requests rather than user support reports. | **INFERENCE:** there is little public evidence of real-world operator feedback, a security response process, compatibility policy, or stable public API. |
| Quality controls | **VERIFIED:** CI compiles Python, enforces only 45% backend line coverage, builds/tests the frontend, and runs Playwright. Actions are version-tag pinned, not commit-SHA pinned. The frontend test step pipes Vitest through `|| true` and then infers failure from log glyphs/strings. See [CI workflow](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/.github/workflows/ci.yml). | **INFERENCE:** the test inventory is useful, but the threshold and brittle log parsing are not a sufficient foundation assurance gate. Supply-chain hardening and deterministic dependency resolution need work. |
| Repository hygiene | **VERIFIED:** generated Vite dependency-cache content, Vitest reports/logs, test results, and a Playwright storage-state JSON are committed in the public tree. The Dockerfile uses `npm install`, although a lockfile exists. | **INFERENCE:** generated artifacts increase noise and stale/binary risk; committed browser auth state is an unsafe pattern even if the current values are test-only. |

**Maintenance verdict:** promising prototype/early project, not yet a low-risk platform dependency for a public financial product.

## 2. Current architecture

### 2.1 Frontend

**VERIFIED:** the frontend is a React 18 + TypeScript single-page application built by Vite. Direct dependencies include TanStack Query, Zustand, React Router, `cmdk`, Headless UI, React Grid Layout, React Mosaic, Lightweight Charts, Recharts, Nivo, D3, React Flow, Three.js, Axios, Fuse.js, Heroicons, and Lucide; versions/ranges are in [`frontend/package.json`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/frontend/package.json). The repository contains a terminal shell, command palette/GO bar, responsive/mobile navigation, launchpad/workspace components, multiple chart systems, and many page-specific modules. Its [`README`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/README.md) describes up to nine synchronized chart panels, 70+ indicators, saved views, and more than 50 pages.

**INFERENCE:** the component breadth is useful for pattern discovery, but overlapping chart, page, route, and terminal component families suggest accretion rather than a narrow reusable design system. ARGUS should not inherit the whole SPA or its route taxonomy.

### 2.2 Backend and background work

**VERIFIED:** the backend is a Python 3.11 FastAPI application served by Uvicorn. The tree includes many API routers and services, provider adapters, APScheduler/background services, WebSocket/SSE paths, backtesting and statistical/ML modules, report generation, plugins, and AI-agent orchestration. The single application image serves the built frontend and backend on port 8000. See the [`Dockerfile`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/Dockerfile), [`backend/main.py`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/backend/main.py), and [`backend/requirements.txt`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/backend/requirements.txt).

**INFERENCE:** a large synchronous/asynchronous API plus in-process jobs, streaming, computation, plugins, and optional local LLMs is convenient for one self-hosting operator but creates coupled scaling, failure, security, and cold-start domains. ARGUS needs explicit web/API/ingestion/worker boundaries even if some initially share a repository or deployment.

### 2.3 Database and cache

**VERIFIED:** SQLAlchemy models and Alembic migrations support SQLite by default and PostgreSQL as an option. Redis supplies cache/quote-bus behavior. Docker Compose mounts local storage and starts Redis; PostgreSQL is an optional profile. See [`docker-compose.yml`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/docker-compose.yml) and the [initial migration](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/backend/alembic/versions/0001_initial.py).

**INFERENCE:** SQLite is acceptable for local single-node evaluation, not the default persistence boundary for concurrent public users and scheduled ingestion. PostgreSQL portability is valuable, but the schema would still need an ARGUS-specific redesign for raw artifacts, observations/vintages, parser versions, validation, lineage, entitlements, quotas, and tenant policies.

### 2.4 Authentication and authorization

**VERIFIED:** users register with email/password; bcrypt hashes passwords; self-registration always assigns `viewer`; roles are `viewer`, `trader`, and `admin`. The service issues HS256 bearer access tokens (15 minutes) and rotating database-recorded refresh tokens (7 days). See [`auth.py`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/backend/equity/routes/auth.py), [`jwt.py`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/backend/auth/jwt.py), and [`user.py`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/backend/models/user.py). Production refuses blank/insecure JWT and cache-signing secrets, while development receives ephemeral secrets ([security configuration](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/backend/config/security.py)).

**VERIFIED CRITICAL DEFECT:** `/api/auth/forgot-access` accepts only an email and a new password and immediately changes the matching account password; it sends no email, verifies no reset token, and requires no existing authentication. Generic handling of unknown emails prevents enumeration but does not prevent account takeover. This endpoint alone makes the authentication system unacceptable for public deployment.

**NOT VERIFIED:** MFA, email verification, breached-password checks, login/reset throttling, CAPTCHA/abuse controls, secure cookie sessions, CSRF defenses (bearer tokens reduce but do not erase browser storage risk), organization/team isolation, row-level security, user deletion/export, consent/privacy workflows, and audited admin role changes were not established by the inspected public evidence.

### 2.5 Data and execution providers

**VERIFIED:** adapters/configuration reference Yahoo Finance/`yfinance`, FMP, Finnhub, FRED, Alpaca, Polygon, Binance WebSocket, Zerodha Kite, NSE-related Python packages/scrapers, and mock/fallback providers. Optional AI routes target OpenAI-compatible services, OpenRouter, Gemini, Ollama, and LM Studio. The provider list is visible in the [environment template](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/.env.example), requirements, and [`backend/adapters`](https://github.com/Hitheshkaranth/OpenTerminalUI/tree/fc16fd646405aec7a5525387be89c0cb376137c5/backend/adapters).

Material provider constraints checked on 2026-08-15:

- **Yahoo/yfinance:** `yfinance` explicitly describes itself as an unaffiliated open-source tool intended for research/education and reminds users Yahoo data is intended for personal use; it is not a redistribution license ([official yfinance project page](https://pypi.org/project/yfinance/), accessed 2026-08-15). **INFERENCE:** unsuitable as the legal basis of a public shared ARGUS market-data service without separate rights.
- **FRED:** the official API requires an API key, and FRED warns that some series may have third-party restrictions ([FRED API terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html), accessed 2026-08-15). Each series still needs rights/provenance handling.
- **Finnhub:** product availability and limits are plan-dependent; the official [pricing page](https://finnhub.io/pricing) is the controlling live source (accessed 2026-08-15). No repository default proves public redistribution rights.
- **FMP:** access, quotas, display, and redistribution depend on the selected plan and terms ([FMP terms](https://site.financialmodelingprep.com/terms-of-service), accessed 2026-08-15). An optional key is not a data-rights strategy.
- **Alpaca:** market-data coverage/feeds and use are subscription/agreement dependent ([official market-data documentation](https://docs.alpaca.markets/docs/about-market-data-api), accessed 2026-08-15).
- **Zerodha Kite:** this is a paid developer product connected to an individual brokerage account, with documented rate limits ([official pricing](https://kite.trade/), [rate limits](https://kite.trade/docs/connect/v3/exceptions/#api-rate-limit), accessed 2026-08-15). It is not a zero-cost public shared feed.
- **OpenRouter/hosted LLMs:** “free” model identifiers are availability- and rate-limit-dependent and send prompts/data to a third party. The official [limits documentation](https://openrouter.ai/docs/api-reference/limits) was checked 2026-08-15. ARGUS cannot make them a required availability, privacy, or zero-cost dependency.

### 2.6 Deployment

**VERIFIED:** the supported full deployment is a multi-stage Docker image plus Redis and optional PostgreSQL in Docker Compose. GitHub Pages publishes only a static landing directory, not the terminal backend ([Pages workflow](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/.github/workflows/pages.yml)). Local AI instructions assume host-side LM Studio/Ollama and potentially large models.

**INFERENCE:** deployment is self-host-first, not a public free-tier reference architecture. A normal always-on container host, persistent volume, Redis, PostgreSQL, background jobs, WebSockets, and optional compute-heavy models create cost and operations obligations.

## 3. Features ARGUS could potentially reuse

“Reuse” below means evaluate a bounded design or implementation behind an ARGUS-owned contract, preserving license notices where code is used. It does not mean transplanting the application.

1. **Terminal shell mechanics:** keyboard command palette, command routing, shortcut help, dense status bars, and responsive navigation.
2. **Workspace mechanics:** React Grid Layout/Mosaic patterns, saved layout serialization, pop-out/split panels, and synchronized symbol/crosshair context. ARGUS should adapt these to a versioned context bus and accessibility requirements.
3. **Chart interaction patterns:** multi-panel charting, range controls, comparisons, drawing persistence, export, replay, and freshness overlays. Validate Lightweight Charts licensing/attribution for the selected version; its official repository is [Apache-2.0](https://github.com/tradingview/lightweight-charts) (accessed 2026-08-15).
4. **Dense analytical tables:** virtualizable screeners, filter chips, formula builders, “why ranked” explanations, heatmaps, and detail drawers.
5. **Portfolio/research workflows:** holdings views, allocation/correlation/risk panels, journal, paper trades, backtest robustness reports, and saved research artifacts—after independent financial-methodology validation.
6. **Provider adapter concept:** abstract provider contracts, registry/failover concepts, service status, and cache TTL policies. ARGUS must replace the provider set and make provenance/rights first-class.
7. **Operational UX:** data-quality and operations dashboards, stale/error states, health indicators, alert builder/delivery concepts, and audit views.
8. **Test ideas:** the broad unit/E2E scenario inventory can inform ARGUS acceptance cases, although ARGUS must write independent tests against its own contracts.

Before reusing any source, isolate the smallest candidate, review its commit history and transitive licenses, scan it, write an ADR, and compare the integration cost against implementing the behavior with the underlying maintained library.

## 4. Features and UI patterns ARGUS must not adopt

| Do not adopt | Reason |
|---|---|
| “Bloomberg-style” GO bar/function-key naming or a look-alike shell as ARGUS identity | ARGUS requires its own commands and trade dress. Workflow inspiration is acceptable; proprietary mimicry is not. |
| Home as a feature launch grid, profile-completion ring, AI Market Outlook, or AI-first mission control | ARGUS Home must answer cross-asset and Pakistan-market questions quickly, with official facts and freshness dominant. Marketing/AI panels dilute that hierarchy. |
| Repeated KPI/metric-card mosaics and equally weighted panels | ARGUS calls for compact tables, precise hierarchy, resizable analytical panels, and restrained surfaces rather than a generic dashboard. |
| India/US equity and F&O taxonomy as primary navigation | ARGUS begins with Pakistan fixed income, macro, FX/money markets, auctions, and global context. Information architecture must follow ARGUS users and lawful data. |
| Claims such as “real-time,” “live,” “institutional-grade,” analyst estimates, order book, or consensus without entitlement/source/freshness proof | Such labels can mislead users and create licensing exposure. Every value needs observation type, source, timestamp, delay/status, and permitted use. |
| AI emotion, multi-agent debate, conviction scores, or AI risk verdicts mixed visually with factual market data | ARGUS must separate `FACT`, `CALCULATED`, and `ARGUS VIEW`; optional AI must be grounded, auditable, scoped, and never imply official status. |
| Real-order/OMS/hotkey execution concepts in the initial product | ARGUS initial trading is paper-only. Broker adapters remain disabled boundaries unless separately approved and secured. |
| Alternative technical charts, 3D/Three.js visuals, decorative gauge/radar proliferation, and crypto-first visual language | These add bundle/maintenance cost and visual noise before core rates/provenance workflows. Adopt only where a validated analytical task requires them. |
| Fake/fallback provider data displayed as ordinary market data | Demo data must be isolated and prominently labeled `DEMO`; failures must degrade to traceable last-known-good data, not plausible substitutes. |
| Client-stored bearer-token auth and the existing password-reset flow | Public ARGUS needs a reviewed identity/session architecture and secure, time-limited, single-use recovery. |

## 5. Pakistan fixed-income and official-data gaps

**VERIFIED:** no `Pakistan`, `SBP`, `InvestPak`, `PSX`, `KIBOR`, `PIB`, `MTB`, or `Sukuk` path was present in the inspected repository tree. The README's market emphasis is NSE/BSE and US markets; the fixed-income area exposes a generic bond calculator and yield-curve dashboard. No official-Pakistan provider is configured in the environment template or direct dependencies.

OpenTerminalUI therefore lacks the foundations for ARGUS's flagship domain:

- canonical modelling for MTBs, fixed/floating/zero-coupon PIBs, PFLs, and Government Ijara Sukuk, including instrument terms, calendars, day counts, cash flows, and official identifiers;
- SBP/InvestPak auction calendars and results with targets, bids, accepted amounts, cut-offs, weighted averages, non-competitive bids, methodology-labelled bid-to-cover, raw-file retention, and corrections;
- official secondary/reference curve ingestion, missing-tenor handling, historical comparisons, basis-point changes, spread histories, and transparent curve-regime classification;
- SBP policy corridor, KIBOR bid/offer/mid, OMO injections/mop-ups and maturities, liquidity, money/credit, FX/reserves, and official release metadata;
- PBS inflation vintages/revisions and official Pakistan macro/fiscal/external datasets;
- source registry, retrieval/observation/publication times, raw artifact hashes, parser version, validation state, revision lineage, and licensing/redistribution fields;
- Pakistan calendars, settlement conventions, localized aliases, and data-quality fixtures for changing Excel/PDF/HTML releases.

**INFERENCE:** these are core domain and data-model changes, not additional screens or a few adapters. Grafting them onto the existing equity/trading-centered schema would likely preserve the wrong abstractions.

Primary official starting points, verified available 2026-08-15, are the [SBP Economic Data portal](https://www.sbp.org.pk/ecodata/index2.asp), [SBP Financial Markets data area](https://www.sbp.org.pk/dfmd/), [InvestPak](https://investpak.sbp.org.pk/), [Pakistan Bureau of Statistics](https://www.pbs.gov.pk/), [Ministry of Finance](https://www.finance.gov.pk/), and [PSX Data Portal](https://dps.psx.com.pk/). Availability does **not** by itself establish automated access, caching, historical storage, or redistribution rights; each dataset needs a dated rights record and parser feasibility test.

## 6. Multi-user and public-product gaps

OpenTerminalUI has accounts and owner-linked records, so it is beyond a purely anonymous desktop. It is not yet a sufficient public multi-user product boundary.

- **Identity:** critical unauthenticated password replacement; no verified email ownership, secure recovery, MFA, session/device management, or mature abuse protection.
- **Authorization:** three coarse roles do not cover ARGUS anonymous, registered, contributor/researcher, moderator, and administrator states. There is no verified deny-by-default permission matrix.
- **Isolation:** model-level `user_id` fields do not prove object-level authorization on every route. No independent tenant-isolation test report or database row-level security was found.
- **Public access:** auth middleware exempts broad `/api/v1` and `/api/public` prefixes in [`backend/auth/deps.py`](https://github.com/Hitheshkaranth/OpenTerminalUI/blob/fc16fd646405aec7a5525387be89c0cb376137c5/backend/auth/deps.py); each route still requires a separate data exposure and resource-exhaustion audit.
- **Quotas/abuse:** no verified per-user/public hard quotas for expensive screens, exports, backtests, AI, alerts, uploads, or upstream calls; no demonstrated zero-spend circuit breaker.
- **Privacy/compliance:** no verified privacy notice, retention/deletion/export policy, consent/audit scheme, email delivery controls, moderation/reporting, or data-processing inventory.
- **Collaboration:** saved views exist, but public/private sharing, immutable snapshots, comments, moderation, organizations, and future team boundaries are not demonstrated.
- **Operations:** local bootstrap admin and self-host assumptions do not replace controlled provisioning, audit logging, backups/restores, incident response, and secret rotation.

## 7. Free-tier and deployment limitations

1. **No full static deployment.** GitHub Pages can host the landing/static frontend only. FastAPI, WebSockets, scheduled ingestion, database writes, Redis, and compute require server-side services.
2. **Always-on process mismatch.** The Docker/Compose topology expects a long-running container and local persistent volume. Scale-to-zero platforms introduce cold starts and may suspend workers; serverless request runtimes do not naturally host in-process schedulers or durable WebSockets.
3. **Stateful services multiply quotas.** A public deployment needs managed PostgreSQL, cache/queue, object/raw-file storage, job execution, outbound bandwidth, email, logs, and backups—not merely a free web host.
4. **Resource-heavy image.** Pandas, PyArrow, SciPy, scikit-learn, XGBoost, Statsmodels, HMMlearn, Optuna, report/PDF tooling, Playwright-related flows, and optional local models increase build size, RAM, CPU, and cold-start pressure.
5. **Free upstream data is not a shared-feed license.** Personal-use libraries and key-based free plans can impose attribution, caching, display, redistribution, concurrency, and rate restrictions. Per-user upstream fetching magnifies quota exhaustion.
6. **No hard zero-cost envelope is documented.** There is no verified request budget, retention budget, alert/job cap, egress cap, cache policy by rights class, graceful feature degradation, or automatic paid-overage prevention.
7. **Local AI is not free public hosting.** Running LM Studio/Ollama on an operator's computer violates the requirement that production work independently of a user's machine; hosted “free” models provide no durable capacity guarantee.

For comparison, Cloudflare Workers' free plan has explicit daily/request CPU limits and Pages has build/project limits ([Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/), [Pages limits](https://developers.cloudflare.com/pages/platform/limits/), accessed 2026-08-15). Those limits can suit a deliberately designed edge API/static frontend, but do not make this Python/Redis/ML container fit unchanged. Neon and Supabase offer quota-limited database plans with suspension/usage constraints ([Neon plans](https://neon.com/docs/introduction/plans), [Supabase billing](https://supabase.com/docs/guides/platform/billing-on-supabase), accessed 2026-08-15). **INFERENCE:** ARGUS should design to selected current quotas with hard feature ceilings; it should not retrofit OpenTerminalUI and hope the aggregate remains free.

## 8. Security and dependency risks

### Application/security findings

| Severity | Finding | Required disposition |
|---|---|---|
| Critical | Unauthenticated password replacement via `forgot-access`. | **Replace** the recovery flow and invalidate all sessions on verified recovery; do not expose the current endpoint. |
| High | Large API surface, background schedulers, WebSockets, file/PDF/Excel parsing, exports, plugins, formula/script execution, AI tool use, and broker/provider keys create many trust boundaries. | Threat-model and sandbox/disable each boundary; ship only minimum routes. |
| High | Public route-prefix exemptions and development auth toggles make configuration mistakes consequential. | Deny by default, separate test-only code, validate production configuration, and test every object permission. |
| High | No demonstrated public abuse controls or hard compute/upstream quotas. Backtests, screeners, AI, reports, and uploads are denial-of-service/cost vectors. | Per-IP/user quotas, queues, timeouts, size limits, concurrency caps, and kill switches. |
| High | Provider/broker/LLM secrets coexist in one broad backend process; plugins and AI tools expand the blast radius. | Separate secret scopes/workers, outbound allowlists, least privilege, redaction, and audited tool permissions. |
| Medium | Bearer-token browser handling increases theft persistence if XSS occurs; refresh-token rotation is positive but storage/cookie posture needs review. | Prefer reviewed `HttpOnly`, `Secure`, `SameSite` session cookies or equivalent BFF design, with CSRF strategy and CSP. |
| Medium | Remote news, filings, PDFs, Excel, HTML, and model output are untrusted inputs. | Content-size/type limits, decompression limits, parser isolation, SSRF protection, sanitization, and fixture/fuzz tests. |
| Medium | Generated cache/test/auth artifacts committed to the repository can leak state and obscure review. | Remove artifacts, rotate any real credentials, add secret scanning, and enforce ignore rules. |

### Direct dependency assessment

**VERIFIED:** almost every Python requirement is unpinned—only `bcrypt`, and minimums for a few packages, constrain versions. Thus two builds can resolve different code. Frontend direct ranges are locked by a committed npm lockfile for `npm ci`, but the production Dockerfile runs `npm install`; base images and GitHub Actions use mutable major tags. There is no visible Dependabot/Renovate policy, SBOM, license gate, `pip-audit`, `npm audit`, CodeQL, or container scan in CI.

Representative direct-dependency risks (registry/project metadata accessed 2026-08-15):

- `python-jose` + Passlib/bcrypt is a legacy-style custom auth stack; correctness rests on local implementation. Prefer a maintained identity boundary or rigorously pinned/audited libraries.
- `nsetools` and `nsepython` are unofficial NSE access packages ([nsetools on PyPI](https://pypi.org/project/nsetools/), [nsepython on PyPI](https://pypi.org/project/nsepython/)); availability does not confer exchange redistribution rights and upstream HTML/API changes can break them.
- `yfinance` is unofficial/personal-use oriented, as noted above.
- `mibian` is old and specialist; all pricing/Greeks results require independent convention and numerical validation ([PyPI project](https://pypi.org/project/mibian/)).
- `pypdf`, Beautiful Soup, lxml, openpyxl, PyArrow, ReportLab, and multipart upload support process complex untrusted content; parser vulnerabilities and resource exhaustion matter even when libraries are current.
- NumPy/Pandas/SciPy/scikit-learn/XGBoost/Statsmodels/HMMlearn/Optuna materially enlarge the runtime and numerical-validation surface. They should live in bounded analytics workers, not automatically in every web instance.
- `lightweight-charts-indicators` and `oakscriptjs` are comparatively small/ecosystem-specific direct packages; maintenance, license, API stability, and script-sandbox behavior require focused review before any reuse.
- Multiple overlapping visualization libraries (Lightweight Charts, Recharts, Nivo, D3, Three.js, React Flow) increase bundle, accessibility, patching, and design-consistency costs.

**NOT VERIFIED:** a point-in-time vulnerability scan was intentionally not run because the task prohibits dependency installation. Registry metadata alone cannot establish absence of vulnerabilities. Before selective reuse, generate locked hashes/SBOMs, run OSV or equivalent against lockfiles, review transitive licenses, pin immutable build inputs, and scan the built container.

## 9. Adaptation complexity versus a clean modular foundation

These are planning estimates, not bids. One **engineer-week** means a focused experienced engineer week including tests and documentation; official-data/licensing lead time can dominate calendar time.

| Workstream | Adopt/fork OpenTerminalUI | Clean modular ARGUS with selected components | Why |
|---|---:|---:|---|
| Repository reduction, dependency/build hardening | 4–8 | 2–4 | Forking begins by removing/isolating a large surface; clean starts minimal. |
| Identity, sessions, RBAC, isolation, abuse controls | 6–10 | 5–8 | Existing auth cannot be trusted as-is and creates migration work. |
| Provenance-first data model, raw artifacts, vintages, source rights, jobs | 10–16 | 8–14 | Existing persistence is market/trading feature oriented rather than official-data lineage oriented. |
| Pakistan fixed income/macro adapters and analytics | 16–28 | 16–28 | Domain work is mostly greenfield either way; a fork adds schema/navigation impedance. |
| ARGUS shell, workspace/context bus, design system | 8–14 | 10–16 | The fork has useful UI mechanics, but substantial visual/IA replacement is required. Selective components narrow the clean-build gap. |
| Zero-cost deployment/quotas/observability | 6–12 | 5–10 | Existing stateful container topology needs decomposition; clean architecture can target quotas directly. |
| Remove/contain AI, execution, plugins, scrapers, unused routes | 5–10 | 0–2 | Fork-only negative work and continuing merge burden. |
| Security, data-rights audit, migration/regression testing | 8–14 | 6–10 | Larger inherited surface and provider ambiguity increase audit cost. |
| **Indicative foundation total** | **63–112** | **52–92** | Ranges overlap, but the fork has higher inherited risk and long-term merge cost. |

**INFERENCE:** a fork may demonstrate more screens sooner, but “screens visible” is not ARGUS completion. For a tested public Pakistan-rates vertical slice, a clean modular approach is likely 15–30% less foundation effort and materially lower residual risk. Selectively evaluating workspace/chart/table mechanics may save roughly 3–7 engineer-weeks without accepting the entire architecture. The biggest unknown is Pakistan source rights and parser resilience, which neither approach removes.

## 10. Keep / Modify / Replace / Reject matrix

| Area | Decision | ARGUS disposition |
|---|---|---|
| MIT license and notice practice | **KEEP** | Compatible for approved bounded reuse; retain notices and inventory third-party rights. |
| Keyboard palette, shortcuts, status/freshness affordances | **MODIFY** | Use ARGUS commands, accessibility rules, and visual identity; do not mimic proprietary mnemonics. |
| Workspace grid, split panels, linked chart/context concepts | **MODIFY** | Spike underlying libraries; add versioned layouts, ARGUS context entities, persistence, performance, and a11y. |
| Dense tables, screeners, saved views, detail drawers | **MODIFY** | Rebuild around ARGUS entities, provenance, lawful fields, and public quotas. |
| Chart/export/replay interactions | **MODIFY** | Select only necessary parts; centralize formats, source/freshness, accessibility, and licensing attribution. |
| Provider interface/registry concept | **MODIFY** | Keep the abstraction idea; replace contracts with capability, rights, freshness, lineage, rate-limit, and last-known-good semantics. |
| Existing provider implementations and fallback data | **REPLACE** | Use approved official/public ARGUS adapters; never substitute unlabeled mock/plausible data. |
| SQLite-first data model and in-process ingestion | **REPLACE** | Use a multi-user transactional store and durable, idempotent ingestion/job boundaries designed for revisions/provenance. |
| Authentication, recovery, bearer session flow, roles | **REPLACE** | Critical reset defect; implement reviewed identity/session, ARGUS roles, isolation, audit, and abuse controls. |
| Docker Compose local developer experience | **MODIFY** | A local option may be useful; production must use quota-aware independent services and durable storage. |
| Single broad FastAPI runtime with ML/jobs/plugins | **REPLACE** | Keep clean API/domain/worker boundaries and deploy only required capabilities. |
| Portfolio, risk, backtest, journal, paper-trading ideas | **MODIFY** | Treat as workflow references; independently implement/validate finance logic and tenant ownership. |
| AI emotion/debate/conviction as core experience | **REJECT** | Optional later intelligence only, source-grounded and visibly separate from facts. |
| Live OMS/broker execution and trading hotkeys | **REJECT** | Outside initial ARGUS scope and risk envelope; paper workflows only. |
| US/India equity/F&O-first navigation and generic feature grid | **REJECT** | Replace with ARGUS cross-asset and Pakistan fixed-income hierarchy. |
| 3D/decorative/duplicative visualization stack | **REJECT** | Avoid bundle and UI complexity unless a specific analytical acceptance test justifies it. |
| OpenTerminalUI repository as the base/fork | **REJECT** | Selective reference delivers the useful learning without inherited architecture, security, and maintenance liabilities. |

## 11. Final recommendation and next gate

### Recommendation: use it selectively as component/code reference

Do **not** adopt or fork OpenTerminalUI as ARGUS's foundation. It is more useful as a catalog of workflow experiments and test scenarios than as the system boundary for a provenance-led, public Pakistan fixed-income product.

If ARGUS later evaluates reuse, limit it to separate, time-boxed spikes for:

1. command palette/keyboard routing;
2. workspace layout serialization and linked context;
3. chart synchronization/export/freshness overlays;
4. dense screener/table interaction;
5. data-quality/status presentation.

Each spike must compare using the underlying library directly against adapting OpenTerminalUI code, record the exact source commit/license, review transitive dependencies and accessibility, and prove that the result fits an ARGUS-owned interface. Do not import auth, providers, persistence, AI-agent, plugin, scraping, broker execution, or deployment code.

### Short decision summary

OpenTerminalUI is active, MIT-licensed, feature-rich, and worth studying. It is also young, single-maintainer, operationally heavy, provider-rights ambiguous, missing ARGUS's Pakistan/official-data core, and unsafe to expose publicly with its current account-recovery flow. **Reject it as the foundation; selectively reference a few terminal/workspace/chart/table patterns while building ARGUS on a clean modular foundation.**
