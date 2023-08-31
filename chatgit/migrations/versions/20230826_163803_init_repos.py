"""init repos

Revision ID: 8628528dcd58
Revises:
Create Date: 2023-08-26 16:38:03.084688

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import LONGTEXT

# revision identifiers, used by Alembic.
revision: str = "8628528dcd58"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "repositories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("repo_id", sa.Integer),
        sa.Column("name", sa.String(200)),
        sa.Column("full_name", sa.String(200)),
        sa.Column("index_url", sa.String(200)),
        sa.Column("api_url", sa.String(200)),
        sa.Column("description", sa.Text),
        sa.Column("language", sa.String(20), nullable=True),
        sa.Column("has_wiki", sa.Boolean, default=True),
        sa.Column("topics", sa.JSON, nullable=True),
        sa.Column("forks_count", sa.Integer),
        sa.Column("license", sa.JSON),
        sa.Column("readme_content", sa.String(200), nullable=True),
        sa.Column("readme_name", LONGTEXT, nullable=True),
        sa.Column("repo_source", sa.String(10)),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("repositories")
