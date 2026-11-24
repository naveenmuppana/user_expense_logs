from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Budget(Base):
    __tablename__ = "budget"
    __table_args__ = (
        UniqueConstraint("user_id", "category", name="uq_budget_user_category"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Stored lowercase so it lines up with the case-insensitive category totals.
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
            name="fk_budget_user_id_users",
        ),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
