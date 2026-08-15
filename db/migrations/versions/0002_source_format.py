"""Record the declared publisher payload format."""

from alembic import op
import sqlalchemy as sa

revision = "0002_source_format"
down_revision = "0001_data_platform"
branch_labels = None
depends_on = None


def upgrade():
    # 0001 historically used current metadata, so a fresh install may already
    # contain this column while an upgraded installation does not.
    columns = {
        item["name"] for item in sa.inspect(op.get_bind()).get_columns("data_sources")
    }
    if "source_format" not in columns:
        op.add_column(
            "data_sources",
            sa.Column(
                "source_format", sa.String(80), nullable=False, server_default="unknown"
            ),
        )


def downgrade():
    columns = {
        item["name"] for item in sa.inspect(op.get_bind()).get_columns("data_sources")
    }
    if "source_format" in columns:
        op.drop_column("data_sources", "source_format")
