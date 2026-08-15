# Manual ingestion runbook

## Source verification record (2026-08-15 UTC)

Live verification was attempted from the implementation environment with a
named, low-impact user agent. Its outbound CONNECT proxy returned HTTP 403 for
every publisher host before a publisher response was received. Consequently,
**no source-specific connector is enabled** and no official observation was
downloaded, parsed, stored, or displayed.

| Source | Exact candidate endpoints checked | Result / restriction |
|---|---|---|
| U.S. Treasury daily par yield curve | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv`; [methodology](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/treasury-yield-curve-methodology); [policy](https://home.treasury.gov/about/general-information/website-policies-notices) | **DEFERRED/DISABLED**. Proxy 403 prevented verification of response format, methodology, timing, and current policy. |
| SBP policy rate | `https://www.sbp.org.pk/ecodata/policy_rate.asp`; [disclaimer](https://www.sbp.org.pk/other/Disclaimer.htm) | **DEFERRED/DISABLED**. No raw-document distribution or bulk public series API; endpoint and display rights require live review. |
| SBP KIBOR | `https://www.sbp.org.pk/ecodata/kibor_index.asp`; [disclaimer](https://www.sbp.org.pk/other/Disclaimer.htm) | **DEFERRED/DISABLED**. Never expose raw PDFs or a bulk download/export/feed. Exact daily document format and permitted attributed delayed/EOD display require live review. |

Do not bypass the proxy, guess a URL, use a mirror, or enable a registration to
work around this gate. Reverification must capture status, final URL, media
type, headers, a checksum, methodology and rights text/version, publication
timing, and UTC verification time. Only then add synthetic parser fixtures for
malformed data, changed headers, duplicate releases, missing dates, and stale
data alongside the connector.

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

There is intentionally no scheduler. `python -m argus_api.cli SOURCE` performs
one bounded manual run, and fails closed while a registry entry is disabled.
The ingestion transaction must insert fetch/artifact/run/validation and a new
vintage first; only after all release-level checks are `VALID` may it change
`observations.active_vintage_id`. A rejected/quarantined run remains audit
history and cannot change last-known-good publication.

## Failure display

Serve the previous active validated vintage with its original dates and mark it
`DELAYED` or `STALE`. If none exists, return `N/A`/`SOURCE_UNAVAILABLE`. Parsing
failures must be explicit `PARSING_ERROR`; never emit zero, forward-fill,
interpolate, splice a partial curve, or silently substitute another publisher.
