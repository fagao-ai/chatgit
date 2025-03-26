"""init repos

Revision ID: 8628528dcd58
Revises:
Create Date: 2023-08-26 16:38:03.084688

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TEXT as LONGTEXT

# revision identifiers, used by Alembic.
revision: str = "8628528dcd58"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "repository",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("repo_id", sa.Integer, nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("full_name", sa.String()),
        sa.Column("description", sa.Text),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("homepage", sa.String(), nullable=True),
        sa.Column("has_wiki", sa.Boolean, default=True),
        # sa.Column("topics", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=False),
        sa.Column("forks_count", sa.Integer, nullable=False),
        sa.Column("stargazers_count", sa.Integer, nullable=False),
        sa.Column("license", sa.JSON),
        sa.Column("readme_content", LONGTEXT, nullable=True),
        # sa.Column("readme_name", sa.String(200), nullable=True),
        sa.Column("repo_source", sa.String()),
        sa.Column("organization_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_table(
        "topic",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("repo_id", sa.Integer, nullable=False, index=True),
        sa.Column("name", sa.String(), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_table(
        "organization",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("org_id", sa.Integer, nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("meta", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("repository")
    op.drop_table("topic")
    op.drop_table("organization")
