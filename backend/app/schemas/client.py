from typing import Optional
from pydantic import BaseModel

class ClientBase(BaseModel):
    dni: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class ClientCreate(ClientBase):
    dni: str
    name: str
    phone: Optional[str] = None

class ClientUpdate(BaseModel):
    dni: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class ClientRead(ClientBase):
    id: int

    class Config:
        orm_mode = True