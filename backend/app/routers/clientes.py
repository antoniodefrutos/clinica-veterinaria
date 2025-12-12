from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from ..database import get_db
from ..models.client import Client
from ..schemas.client import ClientCreate, ClientRead
from ..utils.security import require_any_role, get_current_user  # ajusta si tus nombres son distintos

router = APIRouter(prefix="/clientes", tags=["clientes"])

# Listar clientes (ejemplo)
@router.get("/", response_model=List[ClientRead])
def list_clients(db: Session = Depends(get_db), user = Depends(require_any_role("admin", "recepcionista"))):
    return db.query(Client).all()

# Crear cliente — versión corregida para evitar UNIQUE constraint error si ya existe el DNI
@router.post("/", response_model=ClientRead, status_code=status.HTTP_200_OK)
def create_client(payload: ClientCreate, db: Session = Depends(get_db), user = Depends(require_any_role("admin", "recepcionista"))):
    """
    Crea un cliente nuevo. Si ya existe un cliente con el mismo DNI,
    devuelve el cliente existente en lugar de lanzar error por UNIQUE constraint.
    """

    # 1) intentar buscar cliente existente por DNI
    existing = db.query(Client).filter(Client.dni == payload.dni).first()
    if existing:
        # Devolver el cliente existente con 200 OK (idempotencia por DNI)
        return existing

    # 2) si no existe, crear uno nuevo
    new_client = Client(
        dni=payload.dni,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        # address y subscription_id si tu modelo los usa; quítalos si no aplican
        # address=payload.address if hasattr(payload, "address") else None,
        # subscription_id=payload.subscription_id if hasattr(payload, "subscription_id") else None,
    )
    db.add(new_client)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # En caso raro de race condition (otro proceso insertó el DNI justo ahora)
        # leemos el cliente y lo devolvemos
        existing = db.query(Client).filter(Client.dni == payload.dni).first()
        if existing:
            return existing
        # si no lo encontramos, raise general error
        raise HTTPException(status_code=500, detail="Error al crear cliente")
    db.refresh(new_client)
    return new_client

# Endpoint para eliminar cliente (ejemplo, sólo admin)
@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db), user = Depends(require_any_role("admin"))):
    client = db.query(Client).get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(client)
    db.commit()
    return None