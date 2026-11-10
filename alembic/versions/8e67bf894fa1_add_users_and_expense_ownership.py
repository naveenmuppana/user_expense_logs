
"""add users and expense ownership

Revision ID: 8e67bf894fa1
Revises: aa0a43f3c2ae
Create Date: 2026-11-10 14:22:17.498616
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8e67bf894fa1"
down_revision: Union[str, Sequence[str], None] = "aa0a43f3c2ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Create user indexes
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # 3. Add nullable user_id to preserve existing expenses
    op.add_column(
        "expense",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    # 4. Create expense user index
    op.create_index(
        "ix_expense_user_id",
        "expense",
        ["user_id"],
        unique=False,
    )

    # 5. Create named foreign key
    op.create_foreign_key(
        "fk_expense_user_id_users",
        "expense",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Reverse the upgrade operations
    op.drop_constraint(
        "fk_expense_user_id_users",
        "expense",
        type_="foreignkey",
    )

    op.drop_index("ix_expense_user_id", table_name="expense")
    op.drop_column("expense", "user_id")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")

    op.drop_table("users")
