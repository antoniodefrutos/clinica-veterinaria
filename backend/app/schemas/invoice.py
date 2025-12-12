from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import date


class InvoiceBase(BaseModel):
    client_id: int
    date: date
    total: float
    pet_id: Optional[int] = None
    appointment_id: Optional[int] = None
    paid: bool = False

    model_config = ConfigDict(from_attributes=True)

class InvoiceCreate(BaseModel):
    client_id: int
    date: date
    total: float
    pet_id: Optional[int] = None
    appointment_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class InvoiceUpdate(BaseModel):
    total: Optional[float] = None
    paid: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class InvoiceOut(InvoiceBase):
    id: int
    payments: List[dict] = Field(default_factory=list)