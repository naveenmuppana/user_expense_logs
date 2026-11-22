import csv
import io
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import (
    CategorySummary,
    MonthlySummary,
    expense_create,
    expense_response,
    expense_update,
    expense_replace,
)
from app.services import expense_service as service

router = APIRouter(
    prefix="/expense",
    tags=["expense"],
)

SORT_PATTERN = "^(id|amount|created_at|title)$"
ORDER_PATTERN = "^(asc|desc)$"


@router.post(
    "/",
    response_model=expense_response,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    expense_data: expense_create,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = Expense(
        **expense_data.model_dump(),
        user_id=current_user.id,
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@router.get("/", response_model=list[expense_response])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: str | None = Query(default=None, min_length=1, max_length=50),
    min_amount: Decimal | None = Query(default=None, gt=0),
    max_amount: Decimal | None = Query(default=None, gt=0),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    sort_by: str = Query(default="id", pattern=SORT_PATTERN),
    sort_order: str = Query(default="desc", pattern=ORDER_PATTERN),
):
    service.validate_ranges(min_amount, max_amount, start_date, end_date)

    query = service.filtered_query(
        db,
        current_user.id,
        category,
        min_amount,
        max_amount,
        start_date,
        end_date,
    )
    query = service.apply_sort(query, sort_by, sort_order)

    return query.offset(offset).limit(limit).all()


@router.get("/export")
def export_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: str | None = Query(default=None, min_length=1, max_length=50),
    min_amount: Decimal | None = Query(default=None, gt=0),
    max_amount: Decimal | None = Query(default=None, gt=0),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    sort_by: str = Query(default="id", pattern=SORT_PATTERN),
    sort_order: str = Query(default="desc", pattern=ORDER_PATTERN),
):
    service.validate_ranges(min_amount, max_amount, start_date, end_date)

    query = service.filtered_query(
        db,
        current_user.id,
        category,
        min_amount,
        max_amount,
        start_date,
        end_date,
    )
    expenses = service.apply_sort(query, sort_by, sort_order).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "title", "amount", "category", "created_at"])

    for expense in expenses:
        writer.writerow(
            [
                expense.id,
                _csv_safe(expense.title),
                expense.amount,
                _csv_safe(expense.category),
                expense.created_at.isoformat(),
            ]
        )

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="expenses.csv"'
        },
    )


def _csv_safe(value: str) -> str:
    # Neutralise spreadsheet formula injection in user-supplied text.
    if value and value[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


@router.get("/summary/monthly", response_model=list[MonthlySummary])
def monthly_summary(
    year: int = Query(ge=1970, le=9999),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.monthly_totals(db, current_user.id, year)


@router.get("/summary/categories", response_model=list[CategorySummary])
def category_summary(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service.validate_ranges(None, None, start_date, end_date)

    return service.category_totals(db, current_user.id, start_date, end_date)


@router.get("/{expense_id}", response_model=expense_response)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_owned_expense(db, current_user.id, expense_id)


@router.put("/{expense_id}", response_model=expense_response)
def replace_expense(
    expense_id: int,
    expense_data: expense_replace,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = service.get_owned_expense(db, current_user.id, expense_id)

    expense.title = expense_data.title
    expense.amount = expense_data.amount
    expense.category = expense_data.category

    db.commit()
    db.refresh(expense)

    return expense


@router.patch("/{expense_id}", response_model=expense_response)
def update_expense(
    expense_id: int,
    expense_data: expense_update,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = service.get_owned_expense(db, current_user.id, expense_id)

    update_data = expense_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)

    return expense


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = service.get_owned_expense(db, current_user.id, expense_id)

    db.delete(expense)
    db.commit()

    return None
