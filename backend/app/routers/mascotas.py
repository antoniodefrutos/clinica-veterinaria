from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.pet import Pet
from ..schemas.pet import PetCreate, PetOut, PetUpdate

from .auth import get_current_user, require_any_role, require_role

router = APIRouter(prefix="/mascotas", tags=["mascotas"])

# Listar mascotas (autenticado)
@router.get("/", response_model=List[PetOut])
def list_pets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return db.query(Pet).order_by(Pet.id).offset(skip).limit(limit).all()

# Obtener mascota por id (autenticado)
@router.get("/{pet_id}", response_model=PetOut)
def get_pet(pet_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    p = db.query(Pet).filter(Pet.id == pet_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pet not found")
    return p

# Crear mascota (receptionist)
@router.post("/", response_model=PetOut, status_code=status.HTTP_201_CREATED)
def create_pet(payload: PetCreate, db: Session = Depends(get_db), user = Depends(require_role("receptionist"))):
    # Validación: owner existe
    from ..models.client import Client
    owner = db.query(Client).filter(Client.id == payload.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner (client) not found")
    p = Pet(**payload.model_dump())  # Pydantic v2 -> model_dump()
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

# Actualizar mascota (receptionist o veterinarian)
@router.put("/{pet_id}", response_model=PetOut)
def update_pet(pet_id: int, payload: PetUpdate, db: Session = Depends(get_db), user = Depends(require_any_role("receptionist", "veterinarian"))):
    p = db.query(Pet).filter(Pet.id == pet_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pet not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

# Borrar mascota (admin)
@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: int, db: Session = Depends(get_db), user = Depends(require_role("admin"))):
    p = db.query(Pet).filter(Pet.id == pet_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pet not found")
    db.delete(p)
    db.commit()
    return None
