# backend/app/routers/clientes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.client import Client  # archivo app/models/client.py
from ..schemas.client import ClientCreate, ClientRead, ClientUpdate
from ..utils.security import get_current_user  # asume que devuelve User o lanza 401

router = APIRouter(prefix="/clientes", tags=["clientes"])


def _assert_admin(user):
    if not user or not getattr(user, "role", None) or user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/", response_model=List[ClientRead])
def list_clients(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Lista clientes. Requiere token (cualquier rol).
    """
    clients = db.query(Client).order_by(Client.id).all()
    return clients


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Crea cliente. Ahora incluye 'phone' en el schema ClientCreate.
    """
    # evita duplicados por email o dni
    if db.query(Client).filter(Client.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(Client).filter(Client.dni == payload.dni).first():
        raise HTTPException(status_code=400, detail="DNI already registered")

    client = Client(
        dni=payload.dni,
        name=payload.name,
        email=payload.email,
        phone=payload.phone if getattr(payload, "phone", None) else None,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientRead)
def read_client(client_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientRead)
def update_client(client_id: int, payload: ClientUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    # update allowed fields
    if payload.dni is not None:
        client.dni = payload.dni
    if payload.name is not None:
        client.name = payload.name
    if payload.email is not None:
        client.email = payload.email
    # phone is optional in schema; if present, update; if None, keep existing
    if hasattr(payload, "phone") and payload.phone is not None:
        client.phone = payload.phone
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Eliminar cliente: **solo admin**.
    """
    _assert_admin(user)
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    # aquí puedes añadir reglas (p.ej. no borrar si tiene mascotas/facturas)
    db.delete(client)
    db.commit()
    return None