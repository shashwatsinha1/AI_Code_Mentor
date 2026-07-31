"""create problem bank tables

Revision ID: 0003_create_problem_bank_tables
Revises: 0002_create_drafts_table
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_create_problem_bank_tables"
down_revision: str | None = "0002_create_drafts_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "problems",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("starter_code", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_problems_difficulty", "problems", ["difficulty"])
    op.create_index("ix_problems_slug", "problems", ["slug"])
    op.create_index("ix_problems_title", "problems", ["title"])

    op.create_table(
        "test_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("stdin", sa.Text(), nullable=False),
        sa.Column("expected_stdout", sa.Text(), nullable=False),
        sa.Column("is_sample", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("problem_id", "position", name="uq_test_cases_problem_position"),
    )


def downgrade() -> None:
    op.drop_table("test_cases")
    op.drop_index("ix_problems_title", table_name="problems")
    op.drop_index("ix_problems_slug", table_name="problems")
    op.drop_index("ix_problems_difficulty", table_name="problems")
    op.drop_table("problems")
