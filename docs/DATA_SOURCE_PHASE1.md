# Phase 1 real-data source feasibility and rights review

**Initial review date:** 2026-08-15

**SBP policy-rate gate:** 2026-08-16

**Implementation update:** The official Treasury annual CSV route is implemented
as the sole real provider in this slice. SBP policy rate remains a fixture-only,
fail-closed registry contract after live review found a credentialed official
API, non-canonical credential-free pages, and no explicit storage/public-display
permission. KIBOR was not revisited, implemented, or registered in this gate.

**Scope:** this amendment evaluates only official SBP policy-rate routes and
official website/EasyData disclaimers. No SBP credential, adapter, fixture,
ingestion, browser-side provider call, scheduler, or public observation was added.

## Executive decision

| Dataset | Decision | Reason |
|---|---|---|
| State Bank of Pakistan (SBP) policy rate | **DISABLED / NOT SUFFICIENTLY VERIFIED** | The documented EasyData API requires an account/API key; public pages do not provide a current effective-dated observation contract; and official terms do not grant storage/public redistribution. |
| SBP KIBOR | **APPROVE WITH RESTRICTIONS** | Official daily publications are feasible to collect, but their document-oriented delivery is fragile and no explicit grant for bulk storage or public redistribution was established. |
| Official US Treasury daily par yield curve | **IMPLEMENTED / OFFICIAL EOD** | The merged bounded manual CSV slice includes validation, provenance, immutable vintages, and last-known-good promotion. It is not live and has no scheduler. |

The SBP decision authorizes no collection or publication. ARGUS must not offer
an SBP observation, raw file, or series API until the technical and rights gates
are resolved. The pre-existing KIBOR selection is unchanged and outside this
policy-rate-only review.

## Review method and common rules

This review uses publisher-owned pages and policies, rather than aggregators.
On 2026-08-16 the SBP main site and EasyData portal were inspected directly as a
guest. Dynamic session/checksum URLs were observed only to understand the public
flow; they are not treated as stable contracts and were not replayed outside the
site. No access control was bypassed, and no remembered value or third-party
mirror was substituted.

Any later approved adapter must run server-side, identify ARGUS in the user
agent, apply bounded requests/backoff, and never make one upstream request per
user. Store only rights-approved audit material with checksum, retrieval time,
media type, URL, parser version, validation outcome, and ingestion-run ID. A
parse failure must not promote an observation or replace last-known-good data.

### Canonical mapping used by this review

The later canonical contract should keep provider payloads outside the public
API and represent each fact as an immutable observation/vintage:

| Field | Meaning |
|---|---|
| `series_id` | Stable ARGUS identifier, independent of publisher column names. |
| `observation_date` | Publisher's effective/business date, not retrieval date. |
| `observation_time` | Publisher time when explicitly supplied; otherwise null. |
| `value`, `unit` | Decimal value and explicit unit (`PERCENT_PER_ANNUM`). Never binary float. |
| `dimension` | Optional tenor and, for KIBOR, side (`BID`/`OFFER`). |
| `fact_class` | `FACT`; transformations and spreads must be separate `CALCULATED` series. |
| `source_id`, `source_url` | Publisher registry key and exact retrieved URL. |
| `published_at`, `retrieved_at` | Nullable publisher timestamp and UTC ingestion timestamp. |
| `raw_sha256`, `parser_version`, `ingestion_run_id` | Reproducibility lineage. |
| `validation_status` | `VALID`, `QUARANTINED`, or `REJECTED`, with machine-readable reasons. |
| `vintage`, `supersedes_id` | Preserve corrections rather than updating history in place. |
| `rights_id` | Versioned link to the rights decision in this review/ADR. |

Freshness is evaluated in the source's local calendar and timezone. “Stale” is
an operational label, not permission to invent, forward-fill, or silently
switch publishers. Weekends and known holidays extend the next expected date.
Every display must show source, observation date, retrieval time, and freshness.

## 1. State Bank of Pakistan policy rate

### Official route evidence (verified 2026-08-16)

| Official route | Verified behavior | Feasibility consequence |
|---|---|---|
| [Current SBP monetary-policy page](https://www.sbp.org.pk/our-operations/monetary-policy) | Public HTML shows the current policy rate, interest-rate corridor, MPC calendar, and official statement links. The rate display has no effective/observation date. | Useful for human corroboration, but not a canonical observation payload. |
| [Legacy policy-rate URL](https://www.sbp.org.pk/ecodata/policy_rate.asp) | The URL now renders the redesigned SBP home page rather than a dedicated historical table. | The previously proposed HTML-history adapter contract no longer exists. |
| [SBP EasyData](https://easydata.sbp.org.pk/) | Public guest portal identifies policy series `TS_GP_IR_SIRPR_AH.SBPOL0030`, unit `Percent`, frequency `As-Needed`, and provides citation and download UI. The flow uses Oracle APEX session/checksum URLs. At review time the series metadata ended and was last refreshed on 2026-04-28, despite later MPC decisions linked on the main site. | Official provenance exists, but the guest surface was not current and its dynamic UI is not a stable retrieval contract. |
| EasyData documented API | Developer Guide documents `GET https://easydata.sbp.org.pk/api/v1/series/[series_key]/data` with JSON/CSV output. `api_key` is mandatory; an account/login is required; keys expire after 90 days; documented limits are 2,000 requests/day and 250/hour. | Technically structured, but credentials are required and prohibited by this gate. ARGUS must not omit, borrow, or work around the key. |

No official mirror, guessed download URL, policy-statement extraction, or
credential was used. Direct access to `https://www.sbp.org.pk/robots.txt`
returned an access-denied page during review; no attempt was made to bypass it.

### Public website/data-use evidence

The [current SBP disclaimer](https://www.sbp.org.pk/our-operations/disclaimer)
states that content is general information, gives no warranty of accuracy,
currency, availability, or completeness, and may be modified, suspended, or
removed. The current site footer states `Copyright © 2026. All Rights Reserved.`

The EasyData guest disclaimer says data is for information/reference, may be
downloaded at the user's risk, may change or cease to be available, and may
include third-party material. EasyData supplies a citation for the series, but
its footer also states `All Rights Reserved`. Neither official disclaimer grants
ARGUS a licence for systematic retrieval, persistent audit storage, attributed
public display, or redistribution through a public API.

The fact that a value is publicly viewable or downloadable is not treated as
permission for ARGUS's intended public product. This is a feasibility decision,
not legal advice; absent clear official permission, the rights gate fails closed.

### Technical and canonical assessment

ARGUS can technically read the public current-value HTML, but cannot safely map
it to `observation_date` or evaluate event-driven freshness without an effective
date. EasyData provides the desired series identity and metadata, but its stable
machine-readable route is credentialed and its guest observation history was not
current during review. A session-backed guest download is not an acceptable
substitute for the documented API.

Consequently ARGUS cannot currently demonstrate a lawful and reliable path to
retrieve, store provenance for, and publicly display the official policy-rate
observation under this task's constraints.

The intended mapping remains reserved, not implemented:

- `series_id`: `PK.SBP.POLICY_RATE.TARGET`
- `source_id`: `SBP_POLICY_RATE`
- `publisher_series_key`: `TS_GP_IR_SIRPR_AH.SBPOL0030`
- `value`: source decimal; `unit`: `PERCENT_PER_ANNUM`
- `observation_date`: publisher-supplied effective date only
- `observation_time`: null unless explicitly supplied
- `fact_class`: `FACT`

### Freshness, validation, fixtures, and failure gate

Policy-rate freshness is event-driven, not a fixed elapsed-time TTL. A future
adapter must track scheduled/announced MPC decisions and publisher effective
dates. An unchanged decision must not create a duplicate observation. Missing or
conflicting effective dates, stale EasyData metadata, disagreement between
official routes, unknown units, duplicate dates, or values outside
`0 < rate < 100` must quarantine the candidate.

No adapter or fixture is added while the source is disabled. If the gate later
passes, fixtures must be synthetic and cover event changes, unchanged decisions,
duplicate/conflicting effective dates, missing units/dates, schema changes, and
last-known-good preservation. Failed retrieval or validation must never emit an
estimate, infer the rate from corridor bounds or prose, or replace the last
validated observation.

**Exact blocker:** SBP must provide (1) a stable credential-free official
response containing value, unit, effective/observation date, and revision
semantics, and (2) an explicit licence or written permission covering ARGUS's
retrieval, minimum provenance retention, attributed public display, and intended
API exposure.

**Decision: DISABLED / NOT SUFFICIENTLY VERIFIED.**

## 2. State Bank of Pakistan KIBOR

### Source, delivery, and schedule

- **Publisher/official source:** State Bank of Pakistan.
- **Canonical index/archive:** <https://www.sbp.org.pk/ecodata/kibor_index.asp>.
- **Terms/disclaimer review point:** <https://www.sbp.org.pk/other/Disclaimer.htm>.
- **Available format:** HTML archive/index linking official daily PDF
  publications. Individual releases are PDF. No stable official CSV, XLS/XLSX,
  RSS, or documented API is relied on by this decision; discovery of such a
  first-party format during pre-implementation verification should trigger an
  ADR amendment, not an unreviewed substitution.
- **Frequency/timing:** each Pakistan interbank business day. Treat publication
  as expected by 13:00 PKT, but verify the live archive and methodology before
  implementation; run a bounded check shortly after that time and one retry
  later in the business day.

### Rights assessment

The archive and releases are public official publications, appropriate for
linking and for display of the daily bid/offer facts with conspicuous “State
Bank of Pakistan” attribution. The available public materials reviewed here do
not amount to an explicit open-data or bulk-redistribution licence. KIBOR's
benchmark status also warrants more caution than a central-bank policy decision:
ARGUS must not imply that it calculates, contributes to, or licenses KIBOR.

**Restriction:** retain source PDFs only in a private audit cache; display
validated values, observation date, tenor, side, source link, and delayed/EOD
status. Disable raw-PDF redistribution, data dumps, downstream feeds, and public
bulk API access. Reconfirm the live disclaimer and seek written SBP permission
before enabling export or systematic third-party redistribution.

### Collection and mapping

Use the HTML index only to discover the exact same-day SBP PDF URL. Allowlist
`https://www.sbp.org.pk/`, reject cross-origin links, and fetch at most the newly
published document. Store the original PDF privately, verify PDF signature and
content type, then use deterministic table extraction. Do not OCR by default;
an image-only or structurally changed PDF is quarantined for manual review.

Map every stated tenor/side pair as an observation:

- `series_id`: `PK.SBP.KIBOR.<TENOR>.<SIDE>`
- `dimension.tenor`: canonical ISO-like values (`1W`, `2W`, `1M`, `3M`, `6M`,
  `9M`, `1Y`) only when actually present
- `dimension.side`: `BID` or `OFFER`; never invent a midpoint
- `observation_date`: rate date printed in the release
- `value`: quoted percentage; `unit`: `PERCENT_PER_ANNUM`
- `source_id`: `SBP_KIBOR`; `fact_class`: `FACT`

### Freshness, validation, fixtures, and failure

- **Fresh:** latest validated publication for the current Pakistan interbank
  business day once released.
- **Pending/delayed:** retain the prior business day's observation before the
  expected publication deadline and label it with its actual date.
- **Stale:** no validated new publication by 17:00 PKT on an expected business
  day, or the Pakistan calendar cannot determine whether a release is due.

Risks include changing archive paths, PDFs with positioned text rather than a
real table, font encoding, scanned documents, wrapped headers, bid/offer column
reversal, tenor additions/removals, amended same-date files, decimals parsed as
dates, holidays, and methodology changes. Require the printed date to match the
expected archive date; a unique canonical tenor set; `0 < bid <= offer < 100`;
no duplicate tenor/side; and plausible day-on-day movement configured as a
review threshold, never an automatic correction. A changed checksum for the
same date creates a new vintage and manual alert.

Commit only synthetic minimal PDF fixtures generated by ARGUS (not copied SBP
documents), plus expected parse output and metadata. Cover valid text tables,
reordered/noisy text, missing tenor, reversed spread, duplicate date, image-only
PDF, changed checksum, and parser failure. A private integration fixture may be
checksum-pinned subject to the rights restriction and access controls.

Failures retain the complete last-known-good curve with original observation
date; never combine tenors from different dates. Mark the dataset
`SOURCE_ERROR`, and `STALE` after the deadline. If only some rows validate,
quarantine the entire daily release rather than publishing a partial curve.

**Suitability:** suitable for an attributed, delayed/EOD free public display,
but not yet for export or redistribution as a feed. **Decision: APPROVE WITH
RESTRICTIONS.**

## 3. Official US Treasury daily par yield curve

### Source, delivery, and schedule

- **Publisher/official source:** US Department of the Treasury.
- **Human-readable page:**
  <https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve>.
- **Official CSV route (year parameter shown):**
  <https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv>.
- **Official XML feed (year parameter shown):**
  <https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value=2026>.
- **Methodology:**
  <https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/treasury-yield-curve-methodology>.
- **Website policy:**
  <https://home.treasury.gov/about/general-information/website-policies-notices>.
- **Available format:** HTML, CSV, and XML. No PDF, XLS/XLSX, RSS, or documented
  JSON API is required. The parameterized CSV/XML services are downloads/feeds;
  do not market them as a guaranteed REST API.
- **Frequency/timing:** one observation for each US federal business day,
  generally published near 18:00 US Eastern Time. Poll once after 18:30 ET and
  retry with backoff; verify the site's stated timing before implementation.

The rates are official daily par yield curve estimates, not executable,
intraday, constant-maturity, or end-user bond quotes. ARGUS must use that full
label and show the observation date.

### Rights assessment

Treasury's website policy states the general US-government rule that material
created by the federal government is not copyright-protected in the United
States, while warning that third-party or otherwise identified material can be
restricted. This dataset is published by Treasury and no third-party legend is
identified in the source selection. Accordingly ARGUS may access, cache, store,
display, attribute, and publicly redistribute the factual observations, subject
to preserving any notices discovered during the pre-implementation recheck,
not implying Treasury endorsement, and not using Treasury seals/logos.

Attribute as “U.S. Department of the Treasury,” link the methodology and source
download, and label any ARGUS interpolation/spread as `CALCULATED`. This is not
legal advice; a changed notice or third-party legend pauses redistribution.

### Collection and mapping

Prefer the official CSV because it is simple, bounded by calendar year, and
testable. Request the current year on schedule and the previous year only at the
year boundary or during a deliberate backfill. Use conditional GET, retain raw
bytes/checksum, and parse by normalized maturity header—not column position.
Use XML only as a separately tested operational fallback after recording the
fallback source URL and equivalent methodology; disagreement quarantines the
date rather than blending formats.

- `series_id`: `US.UST.PAR_YIELD.<TENOR>`
- `dimension.tenor`: `1M`, `1.5M` (six weeks), `2M`, `3M`, `4M`, `6M`, `1Y`,
  `2Y`, `3Y`, `5Y`, `7Y`, `10Y`, `20Y`, or `30Y`, only where the source
  actually publishes that maturity for the date
- `observation_date`: `Date` in US Eastern calendar
- `value`: published rate; `unit`: `PERCENT_PER_ANNUM`
- `source_id`: `UST_DAILY_PAR_YIELD_CURVE`; `fact_class`: `FACT`

Do not backfill a maturity before Treasury began publishing it, interpolate a
blank, or confuse the par curve with Treasury real, bill, long-term, or
constant-maturity rate datasets.

### Freshness, validation, fixtures, and failure

- **Fresh:** latest validated observation is for the latest expected US federal
  business day, allowing the publication window.
- **Pending:** before 20:00 ET on that business day, show the prior observation
  with its date rather than calling it current.
- **Stale:** no validated current-business-day row by 20:00 ET. Federal holidays
  and weekends advance the next expected observation instead of aging the last
  valid business day incorrectly.

Risks include Drupal route/query changes, HTML error pages returned with status
200, a changed CSV dialect/BOM, header renaming, newly added maturities, blank
historical cells, duplicate/corrected dates, calendar edge cases, and mixing
curve types. Require expected media/signature, exactly one row per date, known
and uniquely mapped headers, `0 < rate < 30`, and a coherent tenor count for the
date's historical regime. Large daily moves generate review alerts but are not
“fixed.” Same-date changed content creates a new vintage.

Commit a short, hand-minimized CSV fixture with clearly synthetic values and
the same schema, plus XML only if fallback support is approved. Cover BOM/CRLF,
blank historical tenor, added/unknown header, duplicate date, out-of-range
value, HTML masquerading as CSV, year boundary, revision, and partial row. The
public-domain status permits source-derived fixtures, but synthetic values keep
tests independent of current markets.

On failure, retain and serve the complete last-known-good date with explicit
observation/retrieval timestamps. Mark `SOURCE_ERROR`, then `STALE` after the
deadline. Never splice maturities, forward-fill, estimate, or silently use a
Federal Reserve/third-party series.

**Suitability:** technically, operationally, and legally suitable for the free
public ARGUS product with attribution and policy monitoring. **Decision:
APPROVE FOR IMPLEMENTATION.**

## Implementation gate for the next phase

Before code is accepted, the implementing change must (1) live-verify every
selected endpoint, media type, publication timing, methodology, and rights page;
(2) capture the verification date and exact policy text/version in a source
registry; (3) obtain maintainer/legal sign-off on the SBP restrictions; (4)
define Pakistan and US business calendars; (5) add deterministic parser,
validation, freshness, revision, and last-known-good tests; and (6) demonstrate
that no browser request, fabricated fallback, cross-source substitution, or raw
SBP redistribution is possible.
