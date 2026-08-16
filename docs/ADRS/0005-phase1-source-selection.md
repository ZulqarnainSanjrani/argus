# ADR 0005: Phase 1 official-source selection

- **Status:** Accepted; amended after SBP policy-rate feasibility gate
- **Date:** 2026-08-15
- **Last amended:** 2026-08-16

## Context

ARGUS needs real-data vertical slices without weakening provenance, licensing,
or no-fabrication rules. The initial source-selection review considered the SBP
policy rate, SBP KIBOR, and the U.S. Treasury daily par yield curve. The merged
repository has since implemented the Treasury selection as a bounded official
EOD vertical slice. This amendment records that implementation and the result
of a new gate focused only on SBP policy rate.

The detailed source evidence, route behavior, rights review, canonical mapping,
freshness rules, and failure behavior are recorded in
[`../DATA_SOURCE_PHASE1.md`](../DATA_SOURCE_PHASE1.md). The operational state is
recorded in [`../INGESTION_RUNBOOK.md`](../INGESTION_RUNBOOK.md).

## Decision

### U.S. Treasury daily par yield curve — implemented

The official yearly CSV selection is already merged as ARGUS's first real-data
vertical slice. The implementation provides a manual server-side connector,
synthetic CSV fixture, decimal validation, raw checksum and optional artifact
retention, immutable fetch/run/vintage provenance, atomic promotion, a
last-known-good pointer, canonical snapshot publication, and explicit
`OFFICIAL_EOD` classification. It has no scheduler, browser-to-provider call,
credential, paid dependency, or silent fallback. Failed or partial payloads do
not replace a promoted vintage.

The implementation environment did not complete an upstream Treasury fetch,
so the adapter is enabled for bounded manual execution but is not evidence of
continuous source availability or a live feed.

### SBP policy rate — disabled after feasibility gate

The prior `APPROVE WITH RESTRICTIONS` decision is superseded. Keep
`SBP_POLICY_RATE` registered as `FIXTURE_ONLY` with no connector factory and no
public official observation until every blocker below is resolved.

Official routes verified on 2026-08-16:

- `https://www.sbp.org.pk/our-operations/monetary-policy` is a public official
  page that displays the current policy rate and the MPC calendar, but the
  numeric display supplies no effective date or observation timestamp.
- `https://www.sbp.org.pk/ecodata/policy_rate.asp`, formerly treated as the
  canonical HTML history, now renders the redesigned SBP home page at the old
  URL. It is no longer a dedicated policy-rate history contract.
- `https://easydata.sbp.org.pk/` is SBP's official EasyData portal. It exposes
  series key `TS_GP_IR_SIRPR_AH.SBPOL0030`, described as an as-needed percent
  series. The guest series page and download flow are session-backed. At review
  time its metadata ended on 2026-04-28 while the main SBP site linked later MPC
  decisions, so it was not a current last-observation authority.
- EasyData documents a machine-readable series API at
  `GET /api/v1/series/[series_key]/data`, with JSON or CSV output. `api_key` is
  mandatory; obtaining it requires an account/login, and the key expires after
  90 days. Credentials are outside this gate and must not be introduced or
  worked around.

The main SBP disclaimer describes site content as general information, disclaims
accuracy/currency/availability, and reserves the right to change or remove it.
The site footer says `Copyright © 2026. All Rights Reserved.` EasyData permits
users to download data at their own risk and supplies citations, but its
disclaimer and footer do not grant ARGUS permission to retain source material or
redistribute the observation in a public product. Public access and factual
nature alone are not treated as that grant.

The exact blockers are therefore:

1. the only documented structured route requires credentials;
2. the credential-free current-value page lacks a publisher observation or
   effective date needed for canonical provenance and event-driven freshness;
3. the guest EasyData series was not current relative to official MPC material;
4. no stable credential-free download contract was documented for automated or
   repeatable retrieval; and
5. no explicit licence or written permission was found for persistent storage
   and public redistribution by ARGUS.

ARGUS must not scrape the dynamic pages, replay session/checksum parameters,
extract a rate from a policy-statement PDF as an inferred feed, use a mirror,
register credentials, or publish the undated homepage value. Last-known-good
behavior is not applicable until there is a first valid promotable observation;
the public API must continue to return DEMO or `SOURCE_UNAVAILABLE`, never a
guessed SBP value.

### SBP KIBOR — unchanged and outside this amendment

The earlier restricted selection remains unimplemented. It was not researched,
enabled, registered, or otherwise changed by the policy-rate-only gate.

## Consequences

- Treasury is the sole enabled official ingestion provider and remains labelled
  EOD, not live.
- No SBP adapter, fixture, parser, schema change, migration, scheduler, or UI
  observation is added by this gate.
- The provider registry continues to fail closed for `SBP_POLICY_RATE` and now
  reports the current credential, effective-date, freshness, and rights blockers.
- The canonical observation schema remains provider-neutral, but the existing
  ingestion implementation contains Treasury-specific labels and freshness;
  those paths must be generalized only as part of a later approved provider.
- A policy-rate value may not be inferred from the interest-rate corridor or
  from prose, and unchanged decisions may not manufacture duplicate observations.

## Alternatives rejected

- **Parsing the redesigned public page:** rejected because its current-value
  display has no effective date and is not a documented data contract.
- **Automating the EasyData guest UI:** rejected because it relies on dynamic
  session state rather than a stable public interface and the published series
  was not current at review time.
- **Using the documented EasyData API:** deferred because it requires an account
  and API key, which this gate expressly excludes.
- **Using policy statements as the numeric feed:** rejected because doing so
  would require document parsing and semantic inference rather than retrieving
  the canonical observation.
- **Third-party aggregators, mirrors, guessed routes, or access-control bypass:**
  rejected because they weaken authority and violate the gate.
- **Assuming redistribution rights from public access or citation support:**
  rejected because the official materials retain all rights and provide no
  applicable public-data licence.

## Reconsideration gate

Reconsider implementation only after SBP provides both:

1. a stable, credential-free official response containing the policy-rate value,
   effective/observation date, unit, and revision semantics, with repeatable
   media type and route behavior; and
2. an explicit licence or written permission covering ARGUS retrieval, minimum
   audit retention, attributed public display, and the intended API surface.

A later approved implementation must be manual-only and event-driven, use
synthetic fixtures, preserve exact source and rights provenance, validate
decimal rate/date/unit/duplicates, quarantine disagreements, and demonstrate
that a failed or stale run cannot replace last-known-good data.
