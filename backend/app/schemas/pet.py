from typing import Optional
from pydantic import BaseModel

class PetBase(BaseModel):
    name: str
    species: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[int] = 0
    weight: Optional[float] = None
    owner_id: Optional[int] = None

class PetCreate(PetBase):
    name: str
    owner_id: int

class PetUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    owner_id: Optional[int] = None

class PetRead(PetBase):
    id: int

    class Config:
        orm_mode = True