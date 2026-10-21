from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.expense import expense_create,expense_response,expense_update,expense_replace
from app.models.expense import Expense

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
    db: Session = Depends(get_db),
):
    expense = Expense(**expense_data.model_dump())

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense

@router.get("/",response_model=list[expense_response])
def get_expenses(db: Session = Depends(get_db)):
    expenses =db.query(Expense).order_by(Expense.id.desc()).all()
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
