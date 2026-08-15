# ADR 0005: Phase 1 official-source selection

- **Status:** Accepted and partially implemented
- **Date:** 2026-08-15

## Context

ARGUS needs a first real-data vertical slice without weakening its provenance,
licensing, or no-fabrication rules. The candidate datasets are the SBP policy
rate, SBP KIBOR, and the US Treasury daily par yield curve. This ADR selects
sources and boundaries only. It does not introduce ingestion, credentials,
storage, network calls from the application, or changes to the running UI.

The detailed feasibility, source URLs, format inventory, schedules, rights
analysis, canonical mappings, stale rules, validation risks, fixture plans, and
failure behavior are recorded in [`../DATA_SOURCE_PHASE1.md`](../DATA_SOURCE_PHASE1.md).

## Decision

1. **SBP policy rate — APPROVE WITH RESTRICTIONS.** Select SBP's official policy
   rate HTML history. A future server-side adapter may privately cache source
   material and display attributed factual observations. Raw-document mirroring,
   bulk downloads, and a redistributable public series API remain disabled until
   an explicit rights review or written permission supports them.
2. **SBP KIBOR — APPROVE WITH RESTRICTIONS.** Select SBP's official KIBOR archive
   and daily documents. Permit attributed delayed/EOD display and private audit
   storage only. Do not export, redistribute as a feed, imply benchmark
   licensing, or OCR/publish an uncertain release. Rights and live format must
   be reverified before implementation.
3. **US Treasury daily par yield curve — APPROVE FOR IMPLEMENTATION.** Select
   Treasury's official yearly CSV as primary delivery, with its HTML page and
   methodology as documentation. XML may be an explicit, validated fallback,
   never a silent cross-source substitute. Public storage and redistribution of
   the government-created observations are allowed subject to the Treasury site
   policy, identified exceptions, attribution, and no endorsement.

All collection will be scheduled and server-side. Publisher payloads terminate
at replaceable adapters and map to immutable ARGUS observations/vintages with
source URL, dates, retrieval timestamp, raw checksum, parser version, validation
status, and rights reference. The API will expose canonical facts and
provenance—not provider-specific schemas. Failed or partial parses cannot replace
last-known-good data, and stale data cannot be filled, estimated, or silently
substituted.

## Consequences

Implementation note (2026-08-15): the bounded Treasury annual CSV adapter is now
enabled for manual server-side ingestion. A proxy 403 prevented an integration
download in the implementation environment, but the route and contract already
approved in this ADR are implemented and fail closed. SBP policy rate is kept as
an explicit `FIXTURE_ONLY` registry entry; KIBOR is outside this narrow slice.

- ARGUS can test one event-driven central-bank series, one document-delivered
  daily money-market curve, and one machine-readable daily sovereign curve.
- The Treasury source is the lowest-risk first implementation candidate and
  should be built first.
- SBP integrations require a narrower product surface and continuing rights
  work. Their public display must remain feature-gated until the live disclaimer,
  timing, formats, and attribution are verified and recorded.
- Source-specific parsers remain replaceable. Canonical series identifiers,
  validation, revisions, calendars, provenance, and freshness are shared domain
  responsibilities rather than UI or adapter behavior.
- No source call may originate in the browser, and no missing value may be
  represented by a fake fallback.

## Alternatives rejected

- **Third-party aggregators or mirrors:** rejected because they weaken authority,
  introduce additional licensing/redistribution questions, and can diverge from
  the official observation.
- **Scraping broad site areas or guessing file URLs:** rejected as brittle,
  unnecessarily burdensome, and inconsistent with the bounded-adapter rule.
- **Using policy statements as the policy-rate feed:** rejected because prose/PDF
  extraction is less robust; statements are corroborating provenance only.
- **Calculating a KIBOR midpoint:** rejected because it would replace two official
  facts with an ARGUS-derived value. A later midpoint must be a separately
  labelled `CALCULATED` series.
- **Federal Reserve or market quotes as Treasury fallback:** rejected because
  their methodology and meaning are not identical to the official Treasury par
  yield curve.
- **Unrestricted SBP redistribution:** deferred, not assumed from public access;
  it requires a clearer licence or permission.

## Follow-up gate

Implementation requires a fresh, successful server-side verification of exact
URLs, response formats, timing, methodology, and rights notices; a versioned
source-rights registry; reviewed business calendars; synthetic fixtures; and
tests for parsing, validation, revisions, freshness, and last-known-good
behavior. Any material difference from this record requires an ADR amendment.
