# backend/app/schemas/appointment.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppointmentBase(BaseModel):
    date: Optional[datetime] = None
    reason: Optional[str] = None
    veterinarian: Optional[str] = None
    pet_id: Optional[int] = None
    client_id: Optional[int] = None

    model_config = {"from_attributes": True}

class AppointmentCreate(AppointmentBase):
    date: datetime
    pet_id: int
    client_id: int

class AppointmentUpdate(BaseModel):
    date: Optional[datetime] = None
    reason: Optional[str] = None
    veterinarian: Optional[str] = None

    model_config = {"from_attributes": True}

class AppointmentOut(AppointmentBase):
    id: int
    model_config = {"from_attributes": True}
