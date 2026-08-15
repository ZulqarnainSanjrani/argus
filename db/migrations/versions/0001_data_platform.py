"""Canonical immutable data platform tables."""
from alembic import op
import sqlalchemy as sa

revision = "0001_data_platform"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Models are the reviewed schema authority; create_all keeps this initial migration
    # equivalent on PostgreSQL and migration-test SQLite without dialect-specific SQL.
    from argus_api.db import Base
    from argus_api import models  # noqa: F401
    Base.metadata.create_all(op.get_bind())

def downgrade():
    from argus_api.db import Base
    from argus_api import models  # noqa: F401
    Base.metadata.drop_all(op.get_bind())
