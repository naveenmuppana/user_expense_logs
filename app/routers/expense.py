from fastapi import APIRouter, Depends,status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.expense import expense_create,expense_response,expense_update
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