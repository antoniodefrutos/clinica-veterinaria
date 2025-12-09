from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .payment import PaymentOut

class InvoiceBase(BaseModel):
    client_id: int
    date: Optional[datetime] = None
    total: Optional[float] = 0.0

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    paid: Optional[bool] = None
    total: Optional[float] = None

class InvoiceOut(InvoiceBase):
    id: int
    paid: bool
    payments: List[PaymentOut] = []

    class Config:
        from_attributes = True
