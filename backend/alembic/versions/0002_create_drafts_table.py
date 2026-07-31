"""create drafts table

Revision ID: 0002_create_drafts_table
Revises: 0001_create_auth_tables
Create Date: 2026-07-29
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_create_drafts_table"
down_revision: str | None = "0001_create_auth_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "drafts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "language", name="uq_drafts_user_language"),
    )
    op.create_index("ix_drafts_language", "drafts", ["language"])
    op.create_index("ix_drafts_user_id", "drafts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_drafts_user_id", table_name="drafts")
    op.drop_index("ix_drafts_language", table_name="drafts")
    op.drop_table("drafts")
