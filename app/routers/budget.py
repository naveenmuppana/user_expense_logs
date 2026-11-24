from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.budget import BudgetResponse, BudgetSet, BudgetStatus
from app.services import budget_service as service

router = APIRouter(
    prefix="/budget",
    tags=["budget"],
)


@router.get("/", response_model=list[BudgetResponse])
def list_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.list_budgets(db, current_user.id)


@router.get("/status", response_model=list[BudgetStatus])
def budget_status(
    month: str | None = Query(
        default=None,
        description="YYYY-MM; defaults to the current month (UTC)",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.budget_status(db, current_user.id, month)


@router.put("/{category}", response_model=BudgetResponse)
def set_budget(
    category: str,
    budget_data: BudgetSet,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.set_budget(db, current_user.id, category, budget_data.amount)


@router.delete("/{category}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service.delete_budget(db, current_user.id, category)

    return None
