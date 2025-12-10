# backend/app/routers/mascotas.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.pet import Pet  # archivo app/models/pet.py
from ..schemas.pet import PetCreate, PetRead, PetUpdate
from ..utils.security import get_current_user

router = APIRouter(prefix="/mascotas", tags=["mascotas"])


def _assert_admin_or_recep(user):
    if not user or not getattr(user, "role", None) or user.role.name not in ("admin", "receptionist"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/", response_model=List[PetRead])
def list_pets(db: Session = Depends(get_db), user=Depends(get_current_user)):
    pets = db.query(Pet).order_by(Pet.id).all()
    return pets


@router.post("/", response_model=PetRead, status_code=status.HTTP_201_CREATED)
def create_pet(payload: PetCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # basic validation: owner exists? (optional)
    pet = Pet(
        client_id=payload.client_id,
        name=payload.name,
        species=payload.species,
        breed=payload.breed,
        age=payload.age,
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


@router.get("/{pet_id}", response_model=PetRead)
def read_pet(pet_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


@router.put("/{pet_id}", response_model=PetRead)
def update_pet(pet_id: int, payload: PetUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    if payload.client_id is not None:
        pet.client_id = payload.client_id
    if payload.name is not None:
        pet.name = payload.name
    if payload.species is not None:
        pet.species = payload.species
    if payload.breed is not None:
        pet.breed = payload.breed
    if payload.age is not None:
        pet.age = payload.age
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Borrar mascota: admin o receptionist.
    """
    _assert_admin_or_recep(user)
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    db.delete(pet)
    db.commit()
    return None