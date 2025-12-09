# backend/app/routers/informes.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.invoice import Invoice
from ..models.payment import Payment
from ..models.appointment import Appointment
from ..models.client import Client
from datetime import datetime
# auth dependency
from .auth import get_current_user, require_role

router = APIRouter(prefix="/informes", tags=["informes"])

# Ingresos por periodo (suma de pagos)
@router.get("/ingresos/")
def ingresos(date_from: Optional[datetime] = Query(None), date_to: Optional[datetime] = Query(None), db: Session = Depends(get_db), user = Depends(require_role("admin"))):
    q = db.query(Payment)
    if date_from:
        q = q.filter(Payment.date >= date_from)
    if date_to:
        q = q.filter(Payment.date <= date_to)
    total = sum(p.amount for p in q.all())
    return {"total": total, "currency": "EUR"}

# Citas por veterinario en periodo
@router.get("/citas_por_vet/")
def citas_por_vet(date_from: Optional[datetime] = Query(None), date_to: Optional[datetime] = Query(None), db: Session = Depends(get_db), user = Depends(get_current_user)):
    q = db.query(Appointment)
    if date_from:
        q = q.filter(Appointment.date >= date_from)
    if date_to:
        q = q.filter(Appointment.date <= date_to)
    rows = q.all()
    agg = {}
    for r in rows:
        vet = r.veterinarian or "Sin asignar"
        agg[vet] = agg.get(vet, 0) + 1
    return agg

# Clientes con facturas pendientes
@router.get("/clientes_deudores/")
def clientes_deudores(db: Session = Depends(get_db), user = Depends(get_current_user)):
    invs = db.query(Invoice).filter(Invoice.paid == False).all()
    client_ids = set(inv.client_id for inv in invs)
    clients = db.query(Client).filter(Client.id.in_(client_ids)).all()
    res = [{"client_id": c.id, "name": c.name, "email": c.email} for c in clients]
    return res
