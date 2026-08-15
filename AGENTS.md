# ARGUS Engineering Instructions

ARGUS is a professional multi-user financial markets terminal. Pakistan fixed
income is a primary specialist domain, alongside Pakistan macroeconomics, FX,
global markets, news, analytics, and educational trading tools.

## Product Principles

- Build a credible institutional research and markets workstation, not a generic
  AI dashboard or consumer fintech app.
- Do not copy proprietary Bloomberg, LSEG, Reuters, or Refinitiv assets,
  layouts, data, trademarks, or paywalled content.
- Prefer reliable, freely accessible, properly licensed, and primary data
  sources where available.
- Never fabricate market, macroeconomic, news, or source data.
- Clearly distinguish `FACT`, `CALCULATED`, and `ARGUS VIEW`.
- Show source, observation date, update time, and data freshness where relevant.
- Use basis points for fixed-income yield changes.
- Treat data providers as replaceable adapters.
- Preserve provenance: source URL, publication date, ingestion timestamp, and
  validation status for stored observations.

## Cost and Security

- Do not add paid services, paid dependencies, or mandatory commercial APIs
  without explicitly explaining the cost and receiving approval.
- Never commit API keys, passwords, tokens, database URLs, or secrets.
- Use environment variables for credentials.
- Do not claim that unlimited real-time global market data is available for free.
- Respect source terms, rate limits, copyright, and licensing restrictions.

## UI Direction

- Use a compact, information-dense, desktop-first institutional terminal style.
- Target 1920×1080 first and support 1440px desktop width well.
- Prefer disciplined dark surfaces, precise borders, tabular numerals, compact
  spacing, restrained cyan accents, clear market-change colors, and dense tables.
- Avoid gradients, neon effects, excessive rounded cards, glassmorphism,
  oversized headings, unnecessary whitespace, and decorative animation.
- Do not let AI views visually resemble official factual data.
- Prevent clipping, overlap, and hidden text at all supported desktop widths.

## Engineering Process

- Inspect relevant code and documentation before making changes.
- Make changes in focused phases; do not attempt the entire product at once.
- Keep components reusable and modular.
- Add tests for business logic, data ingestion, and critical UI behaviour.
- Run relevant formatting, linting, type checks, tests, and builds before saying
  work is complete.
- Do not overwrite working features without a documented migration plan.
- Keep documentation updated as architecture changes.
