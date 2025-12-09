# backend/app/schemas/history.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HistoryBase(BaseModel):
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    observations: Optional[str] = None
    created_by: Optional[str] = None

class HistoryCreate(HistoryBase):
    date: Optional[datetime] = None  # opcional, si no se pasa se usa now()

class HistoryOut(HistoryBase):
    id: int
    pet_id: int
    date: datetime

    class Config:
        orm_mode = True
