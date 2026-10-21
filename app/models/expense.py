from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric,String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Expense(Base):
    __tablename__ = "expense"
    id : Mapped[int]=mapped_column(Integer,primary_key=True,index=True)
    title: Mapped[str]=mapped_column(String(150),nullable=False)
    amount : Mapped[Decimal]=mapped_column(Numeric(10,2),nullable=False)
    category :Mapped[str]=mapped_column(String(50),nullable=False)
    created_at :Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    
    