# backend/app/schemas/billing.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PaymentBase(BaseModel):
    invoice_id: int
    amount: float
    method: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True

class InvoiceBase(BaseModel):
    client_id: int
    total: float
    paid: Optional[bool] = False

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    total: Optional[float] = None
    paid: Optional[bool] = None

class InvoiceOut(InvoiceBase):
    id: int
    date: datetime
    payments: Optional[List[PaymentOut]] = []

    class Config:
        orm_mode = True
