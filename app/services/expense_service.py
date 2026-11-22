from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Query, Session

from app.models.expense import Expense

SORT_COLUMNS = {
    "id": Expense.id,
    "amount": Expense.amount,
    "created_at": Expense.created_at,
    "title": Expense.title,
}


def validate_ranges(
    min_amount: Decimal | None,
    max_amount: Decimal | None,
    start_date: datetime | None,
    end_date: datetime | None,
) -> None:
    if min_amount is not None and max_amount is not None:
        if min_amount > max_amount:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="min_amount cannot exceed max_amount",
            )

    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="start_date cannot be later than end_date",
            )


def filtered_query(
    db: Session,
    user_id: int,
    category: str | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> Query:
    # Always restrict results to the owning user.
    query = db.query(Expense).filter(Expense.user_id == user_id)

    if category is not None:
        # Exact case-insensitive match; escape LIKE wildcards in user input.
        escaped = (
            category.strip()
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        query = query.filter(Expense.category.ilike(escaped, escape="\\"))

    if min_amount is not None:
        query = query.filter(Expense.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Expense.amount <= max_amount)

    if start_date is not None:
        query = query.filter(Expense.created_at >= start_date)

    if end_date is not None:
        query = query.filter(Expense.created_at <= end_date)

    return query


def apply_sort(query: Query, sort_by: str, sort_order: str) -> Query:
    sort_column = SORT_COLUMNS[sort_by]

    if sort_order == "desc":
        return query.order_by(sort_column.desc(), Expense.id.desc())
    return query.order_by(sort_column.asc(), Expense.id.asc())


def get_owned_expense(db: Session, user_id: int, expense_id: int) -> Expense:
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == user_id)
        .first()
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return expense


def monthly_totals(db: Session, user_id: int, year: int) -> list[dict]:
    month = extract("month", Expense.created_at)

    rows = (
        db.query(
            month.label("month"),
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        .filter(
            Expense.user_id == user_id,
            extract("year", Expense.created_at) == year,
        )
        .group_by(month)
        .order_by(month)
        .all()
    )

    return [
        {"month": int(r.month), "total": r.total, "count": r.count}
        for r in rows
    ]


def category_totals(
    db: Session,
    user_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[dict]:
    category = func.lower(Expense.category)

    query = db.query(
        category.label("category"),
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("count"),
    ).filter(Expense.user_id == user_id)

    if start_date is not None:
        query = query.filter(Expense.created_at >= start_date)

    if end_date is not None:
        query = query.filter(Expense.created_at <= end_date)

    rows = query.group_by(category).order_by(func.sum(Expense.amount).desc()).all()

    return [
        {"category": r.category, "total": r.total, "count": r.count}
        for r in rows
    ]
