# Database boundary

Alembic owns the reviewed canonical observation, vintage, validation, source,
and ingestion-lineage schema. PostgreSQL is optional for local development and
is configured only through `ARGUS_DATABASE_URL`; no credentials are committed.

The static workstation demo does not require a database. When no configured
database contains a promoted valid observation, the snapshot API falls back to
conspicuously labelled local DEMO data. The dedicated home-workspace demo route
is always synthetic and never queries providers or persistence.
