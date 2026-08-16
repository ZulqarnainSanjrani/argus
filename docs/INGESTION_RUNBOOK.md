# Manual ingestion runbook

## Source verification record

Treasury verification was attempted on 2026-08-15 UTC with a named, low-impact
user agent. The outbound CONNECT proxy returned HTTP 403 before a publisher
response was received, so no official Treasury observation was downloaded. The
already approved CSV contract is enabled for bounded manual ingestion and fails
closed on HTTP, media-type, schema, or value errors. It is not a live feed.

SBP policy-rate routes and disclaimers were inspected directly as a public guest
on 2026-08-16. No observation was downloaded into ARGUS, no account or API key
was created, and no dynamic session route was replayed or automated.

| Source | Exact candidate endpoints checked | Result / restriction |
|---|---|---|
| U.S. Treasury daily par yield curve | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv`; [methodology](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/treasury-yield-curve-methodology); [policy](https://home.treasury.gov/about/general-information/website-policies-notices) | **ENABLED / OFFICIAL EOD** for manual ingestion. Proxy 403 blocked the environment integration check; operational monitoring must retain this limitation and never label the feed live. |
| SBP policy rate | [current monetary-policy page](https://www.sbp.org.pk/our-operations/monetary-policy); [EasyData](https://easydata.sbp.org.pk/), series `TS_GP_IR_SIRPR_AH.SBPOL0030`; [current disclaimer](https://www.sbp.org.pk/our-operations/disclaimer) | **FIXTURE_ONLY / DISABLED**. EasyData's documented JSON/CSV API requires an account/API key. The current public HTML lacks an effective date; the guest EasyData series lagged later MPC decisions; and both official surfaces retain all rights without an explicit ARGUS storage/public-display grant. |

Do not bypass access controls, automate the EasyData guest UI, replay APEX
session/checksum URLs, guess a download route, use a mirror, infer a value from
the corridor or a policy statement, register credentials, or enable the source
to work around this gate. Reverification must capture a stable credential-free
response with value/unit/effective date/revision semantics plus explicit rights
for retrieval, audit retention, attributed public display, and the intended API
surface. Only after both conditions pass may a separately reviewed change add a
manual event-driven connector and synthetic fixtures.

## Local database and migration

```bash
cp .env.example .env
docker compose up -d db
alembic -c db/alembic.ini upgrade head
```

Validate against PostgreSQL (not SQLite) by exporting a disposable test
database URL, applying the migration, and running the integration suite:

```bash
export ARGUS_DATABASE_URL=postgresql+psycopg://argus:argus_local_only@localhost:5432/argus
export ARGUS_TEST_DATABASE_URL="$ARGUS_DATABASE_URL"
alembic -c db/alembic.ini upgrade head
pytest -q apps/api/tests
```

The PostgreSQL tests truncate canonical tables and must never target a shared or
production database. CI separately creates a disposable database to verify
`upgrade head` followed by `downgrade base` without destroying the test schema.

The initial migration creates source, fetch, artifact metadata, run,
validation, series, observation, and vintage tables. Payload bytes are not in
the relational schema. `storage_reference` is private metadata and must never
be made public for restricted SBP artifacts.

## One-shot execution

There is intentionally no scheduler. `python -m argus_api.cli UST_DAILY_PAR_YIELD_CURVE`
performs one bounded manual run; `--dry-run` fetches, parses, and validates without
writing. `ARGUS_DATABASE_URL` is required for publication and
`ARGUS_ARTIFACT_DIR` optionally retains official Treasury CSV bytes by checksum.
The ingestion transaction must insert fetch/artifact/run/validation and a new
vintage first; only after all release-level checks are `VALID` may it change
`observations.active_vintage_id`. A rejected/quarantined run remains audit
history and cannot change last-known-good publication.

## Failure display

Serve the previous active validated vintage with its original dates and mark it
`DELAYED` or `STALE`. If none exists, return `N/A`/`SOURCE_UNAVAILABLE`. Parsing
failures must be explicit `PARSING_ERROR`; never emit zero, forward-fill,
interpolate, splice a partial curve, or silently substitute another publisher.
