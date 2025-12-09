# backend/app/routers/clientes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.client import Client
from ..schemas.client import ClientCreate, ClientOut, ClientUpdate

from .auth import get_current_user, require_role  # auth deps

router = APIRouter(prefix="/clientes", tags=["clientes"])

# Listar clientes (cualquiera autenticado)
@router.get("/", response_model=List[ClientOut])
def list_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return db.query(Client).order_by(Client.id).offset(skip).limit(limit).all()

# Obtener cliente
@router.get("/{client_id}", response_model=ClientOut)
def get_cliente(client_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    return c

# Crear cliente (receptionist o admin) -> receptionists normalmente lo hacen
@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_cliente(payload: ClientCreate, db: Session = Depends(get_db), user = Depends(require_role("receptionist"))):
    # validaciones mínimas
    if db.query(Client).filter(Client.dni == payload.dni).first():
        raise HTTPException(status_code=400, detail="Client with same DNI already exists")
    c = Client(**payload.dict())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

# Actualizar cliente (receptionist)
@router.put("/{client_id}", response_model=ClientOut)
def update_cliente(client_id: int, payload: ClientUpdate, db: Session = Depends(get_db), user = Depends(require_role("receptionist"))):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(c, k, v)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

# Borrar cliente (admin)
@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cliente(client_id: int, db: Session = Depends(get_db), user = Depends(require_role("admin"))):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(c)
    db.commit()
    return None
