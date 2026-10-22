from fastapi import APIRouter, Depends,status,HTTPException,Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.expense import expense_create,expense_response,expense_update,expense_replace
from app.models.expense import Expense
from decimal import Decimal
from datetime import datetime

router = APIRouter(
    prefix="/expense",
    tags=["expense"],

)


@router.post("/",
              response_model=expense_response,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    expense_data: expense_create,
    db: Session = Depends(get_db)
):
    expense = Expense(**expense_data.model_dump())

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense

@router.get("/",response_model=list[expense_response])
def get_expenses(db: Session = Depends(get_db),
    limit :int=Query(default=10,ge=1,le=100),
    offset : int = Query(default=0,ge=0), category: str | None = Query(default=None, min_length=1, max_length=50),
    min_amount: Decimal | None = Query(default=None, gt=0),
    max_amount: Decimal | None = Query(default=None, gt=0),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    sort_by: str = Query(default="id", pattern="^(id|amount|created_at|title)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),):
    query = db.query(Expense)

    # Filter by category
    if category is not None:
        query = query.filter(
            Expense.category.ilike(category.strip())
        )

    # Filter by amount
    if min_amount is not None:
        query = query.filter(Expense.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Expense.amount <= max_amount)

    # Filter by creation date
    if start_date is not None:
        query = query.filter(Expense.created_at >= start_date)

    if end_date is not None:
        query = query.filter(Expense.created_at <= end_date)

    # Validate amount range
    if min_amount is not None and max_amount is not None:
        if min_amount > max_amount:
            raise HTTPException(
                status_code=422,
                detail="min_amount cannot exceed max_amount",
            )

    # Sort using an allowlist of model columns
    sort_columns = {
        "id": Expense.id,
        "amount": Expense.amount,
        "created_at": Expense.created_at,
        "title": Expense.title,
    }

    sort_column = sort_columns[sort_by]

    if sort_order == "desc":
        query = query.order_by(sort_column.desc(), Expense.id.desc())
    else:
        query = query.order_by(sort_column.asc(), Expense.id.asc())

    # Apply pagination after filtering and sorting
    expenses = query.offset(offset).limit(limit).all()

    return expenses



@router.put("/{expense_id}", response_model=expense_response)
def replace_expense(
    expense_id: int,
    expense_data: expense_replace,
    db: Session = Depends(get_db),
):
    expense = db.get(Expense, expense_id)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

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
):
    expense = db.get(Expense, expense_id)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    update_data = expense_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)

    return expense



@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    expense = db.get(Expense, expense_id)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    db.delete(expense)
    db.commit()

    return None
