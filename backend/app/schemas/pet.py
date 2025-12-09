from pydantic import BaseModel
from typing import Optional

class PetBase(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[int] = None
    owner_id: Optional[int] = None

    model_config = {"from_attributes": True}

class PetCreate(PetBase):
    name: str
    species: str
    owner_id: int

class PetUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[int] = None
    owner_id: Optional[int] = None

    model_config = {"from_attributes": True}

class PetOut(PetBase):
    id: int
    model_config = {"from_attributes": True}
