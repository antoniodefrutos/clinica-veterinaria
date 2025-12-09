# backend/app/schemas/invoice.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InvoiceBase(BaseModel):
    client_id: int
    pet_id: Optional[int] = None
    appointment_id: Optional[int] = None
    amount: float
    description: Optional[str] = None
    date: Optional[datetime] = None

    model_config = {"from_attributes": True}

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    pet_id: Optional[int] = None
    appointment_id: Optional[int] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    paid: Optional[bool] = None

    model_config = {"from_attributes": True}

class InvoiceOut(InvoiceBase):
    id: int
    paid: bool

    model_config = {"from_attributes": True}
