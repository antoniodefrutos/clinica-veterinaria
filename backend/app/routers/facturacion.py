# backend/app/routers/facturacion.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.invoice import Invoice
from ..models.payment import Payment
from ..models.client import Client
from ..schemas.invoice import InvoiceCreate, InvoiceOut, InvoiceUpdate
from ..schemas.payment import PaymentCreate, PaymentOut

from .auth import get_current_user, require_role

router = APIRouter(prefix="/facturacion", tags=["facturacion"])


# Crear factura (receptionist)
@router.post("/invoices/", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db), user = Depends(require_role("receptionist"))):
    # validar cliente
    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    inv = Invoice(
        client_id=payload.client_id,
        pet_id=payload.pet_id,
        appointment_id=payload.appointment_id,
        amount=payload.amount,
        description=payload.description,
        date=payload.date
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


# Listar facturas (autenticado, filtrado opcional)
@router.get("/invoices/", response_model=List[InvoiceOut])
def list_invoices(
    client_id: Optional[int] = None,
    paid: Optional[bool] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    q = db.query(Invoice)
    if client_id is not None:
        q = q.filter(Invoice.client_id == client_id)
    if paid is not None:
        q = q.filter(Invoice.paid == paid)
    if date_from:
        q = q.filter(Invoice.date >= date_from)
    if date_to:
        q = q.filter(Invoice.date <= date_to)
    return q.order_by(Invoice.date.desc()).offset(skip).limit(limit).all()


# Obtener factura
@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


# Actualizar factura (receptionist)
@router.put("/invoices/{invoice_id}", response_model=InvoiceOut)
def update_invoice(invoice_id: int, payload: InvoiceUpdate, db: Session = Depends(get_db), user = Depends(require_role("receptionist"))):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(inv, k, v)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


# Borrar factura (admin)
@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db), user = Depends(require_role("admin"))):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(inv)
    db.commit()
    return None


# Crear pago (receptionist) — añade pago y recalcula estado paid automáticamente
@router.post("/payments/", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), user = Depends(require_role("receptionist"))):
    inv = db.query(Invoice).filter(Invoice.id == payload.invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    payment = Payment(invoice_id=payload.invoice_id, amount=payload.amount, method=payload.method, date=payload.date)
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # recompute total paid
    total_paid = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.invoice_id == inv.id).scalar() or 0
    if total_paid >= inv.amount:
        inv.paid = True
    else:
        inv.paid = False
    db.add(inv)
    db.commit()
    db.refresh(inv)

    return payment


# Listar pagos
@router.get("/payments/", response_model=List[PaymentOut])
def list_payments(invoice_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user = Depends(get_current_user)):
    q = db.query(Payment)
    if invoice_id is not None:
        q = q.filter(Payment.invoice_id == invoice_id)
    return q.order_by(Payment.date.desc()).offset(skip).limit(limit).all()
