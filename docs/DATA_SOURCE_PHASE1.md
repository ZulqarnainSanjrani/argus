# Phase 1 real-data source feasibility and rights review

**Review date:** 2026-08-15

**Implementation update:** The official Treasury annual CSV route is implemented
as the sole real provider in this slice. SBP policy rate remains a fixture-only,
fail-closed registry contract because the reviewed HTML route is not a documented
machine-readable interface and redistribution terms remain insufficiently clear.
KIBOR was not implemented or registered in the runtime slice.

**Scope:** source selection only; no source was connected, no credentials were
added, and no ingestion or browser-side request was implemented.

## Executive decision

| Dataset | Decision | Reason |
|---|---|---|
| State Bank of Pakistan (SBP) policy rate | **APPROVE WITH RESTRICTIONS** | The official, low-volume HTML history is technically suitable, but the reviewed public materials do not provide an explicit open-data licence for republishing the complete series. |
| SBP KIBOR | **APPROVE WITH RESTRICTIONS** | Official daily publications are feasible to collect, but their document-oriented delivery is fragile and no explicit grant for bulk storage or public redistribution was established. |
| Official US Treasury daily par yield curve | **APPROVE FOR IMPLEMENTATION** | Treasury provides first-party machine-readable downloads and US federal-government material is generally reusable under the stated site policy, subject to exceptions and attribution. |

These approvals authorize a later, separately reviewed server-side ingestion
slice. They do not authorize browser calls, scraping, or implementation in this
task. In particular, ARGUS must not offer downloadable SBP raw files or a bulk
SBP-series API until the rights question is resolved in writing.

## Review method and common rules

This review uses publisher-owned pages and policies, rather than aggregators.
Exact URLs and conclusions should be rechecked immediately before an adapter is
merged: this environment could not establish a connection to the publisher
hosts during the review, so endpoint behavior and page text were not live-tested.
That limitation is deliberately reflected in the restricted SBP decisions and
in implementation gates below; remembered values or third-party mirrors must
not be substituted.

All three adapters should be scheduled server-side, identify ARGUS in the user
agent, use conditional requests where supported, apply a low request rate with
exponential backoff, and never make one upstream request per user. Store the
received bytes privately with a checksum, retrieval time, media type, URL,
parser version, validation outcome, and ingestion-run ID. A parse failure must
not promote any observation or replace the last-known-good record.

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

### Source, delivery, and schedule

- **Publisher/official source:** State Bank of Pakistan.
- **Canonical public page:** <https://www.sbp.org.pk/ecodata/policy_rate.asp>.
- **Supporting monetary-policy landing page:**
  <https://www.sbp.org.pk/m_policy/index.asp>.
- **Terms/disclaimer review point:** <https://www.sbp.org.pk/other/Disclaimer.htm>.
- **Available format:** HTML table/page. No official CSV, XLS/XLSX, RSS, or
  documented API is relied on by this decision. Monetary Policy Statements may
  also be PDF, but those PDFs are corroboration, not the primary numeric feed.
- **Frequency/timing:** event-driven. A new target rate becomes effective when
  SBP announces a monetary-policy decision; there is no dependable daily release
  time. Poll once on scheduled Monetary Policy Committee decision days after the
  announcement window, once the following Pakistan business morning, and no
  more than daily otherwise.

### Rights assessment

Public access and linking are appropriate. Individual policy-rate facts are
suited to attributed display, and ARGUS may retain the minimum source response
needed for audit and last-known-good operation. However, availability on a
public page is not itself an open-data licence. This review did not establish an
explicit permission for bulk republication of SBP's historical compilation,
mirroring its page, or distributing its raw HTML/PDFs. SBP name and logo must
not imply endorsement.

**Restriction:** display attributed factual observations and derived charts in
ARGUS, link to SBP, and keep raw responses private and access-controlled. Do not
expose raw documents, a bulk download, or a redistributable series API. Before
launch, counsel/maintainer must re-read the live disclaimer and obtain SBP
clarification if public historical export is desired. Record that verification
date in the rights registry.

### Collection and mapping

Use a narrowly scoped HTML-table adapter against the canonical page—not a
general crawler. Fetch at the above cadence, retain bytes/checksum, locate the
table by normalized headers rather than CSS position, parse dates explicitly,
and normalize percentage text to decimal-safe values. Cross-check a new change
against the linked official Monetary Policy Statement; disagreement quarantines
the new row for review rather than choosing one silently.

- `series_id`: `PK.SBP.POLICY_RATE.TARGET`
- `observation_date`: effective date shown by SBP
- `value`: stated rate; `unit`: `PERCENT_PER_ANNUM`
- `observation_time`: null unless SBP states one
- `source_id`: `SBP_POLICY_RATE`; `fact_class`: `FACT`
- statement title/URL: supporting provenance, not the source of an inferred time

### Freshness, validation, fixtures, and failure

- **Fresh:** the latest validated row agrees with the official page and no
  announced decision with a later effective date is outstanding.
- **Pending:** from an announced/scheduled decision until the next Pakistan
  business day at 12:00 PKT if no new effective row appears.
- **Stale:** later than that deadline, or 24 hours after ARGUS learns of an
  official decision but cannot validate the effective rate. An unchanged rate
  after a decision remains a fresh observation only when the official release
  confirms “unchanged”; do not manufacture a duplicate row.

Reject duplicate effective dates with conflicting values, unparseable dates,
missing units, values outside `0 < rate < 100`, multiple candidate tables, or a
history that unexpectedly shrinks. Quarantine rather than guess whether the
page expresses a target, ceiling, floor, or old discount rate.

Fixtures must be small, hand-minimized HTML documents derived from the table
shape with **synthetic, conspicuously non-market values**, saved with source URL,
capture date, expected records, media type, parser version, and a note that the
fixture is test-only and not redistributable source data. Include reordered
columns, footnotes, commas/non-breaking spaces, malformed dates, duplicate rows,
empty cells, and an unrelated table. Keep a checksum-only manifest for any
private golden raw response.

On HTTP, parse, or validation failure, record the failed run, keep serving the
last validated observation with its original date/source, and expose
`STALE`/`SOURCE_ERROR` when the deadline passes. Never emit zero, null-as-zero,
an estimate, or a policy-statement-derived guess.

**Suitability:** suitable for the free public ARGUS product under the display,
attribution, private-cache, and no-bulk-redistribution restrictions above.
**Decision: APPROVE WITH RESTRICTIONS.**

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
