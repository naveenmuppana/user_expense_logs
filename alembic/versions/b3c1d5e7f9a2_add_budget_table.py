"""add budget table

Revision ID: b3c1d5e7f9a2
Revises: 8e67bf894fa1
Create Date: 2026-11-24 10:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b3c1d5e7f9a2"
down_revision: Union[str, Sequence[str], None] = "8e67bf894fa1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "budget",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_budget_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "category", name="uq_budget_user_category"
        ),
    )
    op.create_index("ix_budget_id", "budget", ["id"], unique=False)
    op.create_index("ix_budget_user_id", "budget", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_budget_user_id", table_name="budget")
    op.drop_index("ix_budget_id", table_name="budget")
    op.drop_table("budget")
