# backend/app/schemas/payment.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentBase(BaseModel):
    invoice_id: int
    amount: float
    method: Optional[str] = None
    date: Optional[datetime] = None

    model_config = {"from_attributes": True}

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int

    model_config = {"from_attributes": True}
