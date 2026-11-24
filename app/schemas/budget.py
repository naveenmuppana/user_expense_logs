from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BudgetSet(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class BudgetResponse(BaseModel):
    category: str
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class BudgetStatus(BaseModel):
    category: str
    budget: Decimal
    spent: Decimal
    remaining: Decimal
    over_budget: bool
