from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class expense_create(BaseModel):
    title: str = Field(min_length = 1, max_length = 150)
    amount : Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category :str =Field(min_length=1, max_length=50)
    
    
class expense_update(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    category: str | None = Field(default=None, min_length=1, max_length=50)


class expense_response(BaseModel):
    id: int
    title: str
    amount: Decimal
    category: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)