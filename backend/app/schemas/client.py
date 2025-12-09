# backend/app/schemas/client.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# Pydantic v2: usar model_config en vez de Config.orm_mode
class ClientBase(BaseModel):
    dni: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    model_config = {"from_attributes": True}


class ClientCreate(ClientBase):
    dni: str
    name: str
    email: Optional[EmailStr] = None


class ClientUpdate(BaseModel):
    # todos opcionales para actualizaciones parciales
    dni: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    model_config = {"from_attributes": True}


class ClientOut(ClientBase):
    id: int

    model_config = {"from_attributes": True}

