import re
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.expense import Expense

MONTH_PATTERN = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")


def normalize_category(category: str) -> str:
    normalized = category.strip().lower()

    if not normalized or len(normalized) > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="category must be 1-50 characters",
        )

    return normalized


def month_bounds(month: str | None) -> tuple[datetime, datetime]:
    """Return the [start, end) UTC bounds of a YYYY-MM month (default: now)."""
    if month is None:
        now = datetime.now(timezone.utc)
        year, number = now.year, now.month
    else:
        match = MONTH_PATTERN.match(month)
        if match is None or int(match.group(1)) < 1970:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="month must be in YYYY-MM format",
            )
        year, number = int(match.group(1)), int(match.group(2))

    start = datetime(year, number, 1, tzinfo=timezone.utc)
    if number == 12:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year, number + 1, 1, tzinfo=timezone.utc)

    return start, end


def set_budget(
    db: Session, user_id: int, category: str, amount: Decimal
) -> Budget:
    category = normalize_category(category)

    budget = (
        db.query(Budget)
        .filter(Budget.user_id == user_id, Budget.category == category)
        .first()
    )

    if budget is None:
        budget = Budget(user_id=user_id, category=category, amount=amount)
        db.add(budget)
    else:
        budget.amount = amount

    db.commit()
    db.refresh(budget)

    return budget


def list_budgets(db: Session, user_id: int) -> list[Budget]:
    return (
        db.query(Budget)
        .filter(Budget.user_id == user_id)
        .order_by(Budget.category)
        .all()
    )


def delete_budget(db: Session, user_id: int, category: str) -> None:
    category = normalize_category(category)

    budget = (
        db.query(Budget)
        .filter(Budget.user_id == user_id, Budget.category == category)
        .first()
    )

    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    db.delete(budget)
    db.commit()


def budget_status(db: Session, user_id: int, month: str | None) -> list[dict]:
    start, end = month_bounds(month)

    spent_rows = (
        db.query(
            func.lower(Expense.category).label("category"),
            func.sum(Expense.amount).label("total"),
        )
        .filter(
            Expense.user_id == user_id,
            Expense.created_at >= start,
            Expense.created_at < end,
        )
        .group_by(func.lower(Expense.category))
        .all()
    )
    spent_by_category = {row.category: row.total for row in spent_rows}

    result = []
    for budget in list_budgets(db, user_id):
        spent = spent_by_category.get(budget.category, Decimal("0.00"))
        result.append(
            {
                "category": budget.category,
                "budget": budget.amount,
                "spent": spent,
                "remaining": budget.amount - spent,
                "over_budget": spent > budget.amount,
            }
        )

    return result
