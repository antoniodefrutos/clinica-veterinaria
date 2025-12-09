# backend/app/routers/citas.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..database import get_db
from ..models.appointment import Appointment
from ..models.client import Client
from ..models.pet import Pet
from ..schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate

from .auth import get_current_user, require_any_role, require_role

router = APIRouter(prefix="/citas", tags=["citas"])


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


# Listar citas (autenticado) - opcional filtro por date/veterinarian
@router.get("/", response_model=List[AppointmentOut])
def list_citas(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    veterinarian: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    q = db.query(Appointment)
    if date_from:
        q = q.filter(Appointment.date >= date_from)
    if date_to:
        q = q.filter(Appointment.date <= date_to)
    if veterinarian:
        q = q.filter(Appointment.veterinarian == veterinarian)
    return q.order_by(Appointment.date.desc()).offset(skip).limit(limit).all()


# Obtener cita por id
@router.get("/{cita_id}", response_model=AppointmentOut)
def get_cita(cita_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    c = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return c


# Crear cita (receptionist o veterinarian)
@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_cita(payload: AppointmentCreate, db: Session = Depends(get_db), user = Depends(require_any_role("receptionist", "veterinarian"))):
    # Validaciones: client y pet existen
    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    pet = db.query(Pet).filter(Pet.id == payload.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Fecha no en pasado (comparar en UTC)
    if payload.date:
        now = _now_utc()
        # payload.date may be naive or timezone-aware; normalize
        dt = payload.date
        if dt.tzinfo is None:
            # assume naive are local naive -> convert to UTC naive by interpreting as UTC
            dt = dt.replace(tzinfo=timezone.utc)
        if dt < now:
            raise HTTPException(status_code=400, detail="Cannot create appointment in the past")

    # Evitar solapamiento por veterinario (misma fecha/hora)
    if payload.veterinarian and payload.date:
        conflict = db.query(Appointment).filter(
            Appointment.veterinarian == payload.veterinarian,
            Appointment.date == payload.date
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail="Veterinarian already has an appointment at that time")

    # Crear
    a = Appointment(**payload.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# Actualizar cita (receptionist or veterinarian)
@router.put("/{cita_id}", response_model=AppointmentOut)
def update_cita(cita_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db), user = Depends(require_any_role("receptionist", "veterinarian"))):
    a = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Si se cambia fecha o veterinario, validar como en create
    data = payload.model_dump(exclude_none=True)
    new_date = data.get("date", None)
    new_vet = data.get("veterinarian", None)

    if new_date:
        now = _now_utc()
        if new_date.tzinfo is None:
            new_date = new_date.replace(tzinfo=timezone.utc)
        if new_date < now:
            raise HTTPException(status_code=400, detail="Cannot set appointment in the past")

    vet_to_check = new_vet if new_vet is not None else a.veterinarian
    date_to_check = new_date if new_date is not None else a.date

    if vet_to_check and date_to_check:
        conflict = db.query(Appointment).filter(
            Appointment.veterinarian == vet_to_check,
            Appointment.date == date_to_check,
            Appointment.id != cita_id
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail="Veterinarian already has an appointment at that time")

    # Aplicar cambios
    for k, v in data.items():
        setattr(a, k, v)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# Borrar cita (receptionist or admin)
@router.delete("/{cita_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cita(cita_id: int, db: Session = Depends(get_db), user = Depends(require_any_role("receptionist", "admin"))):
    a = db.query(Appointment).filter(Appointment.id == cita_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(a)
    db.commit()
    return None
