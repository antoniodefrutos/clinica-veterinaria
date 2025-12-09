from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import SessionLocal, get_db   # si tienes get_db, usa ese
from ..models.invoice import Invoice
from ..models.payment import Payment
from ..schemas.invoice import InvoiceCreate, InvoiceOut, InvoiceUpdate
from ..schemas.payment import PaymentCreate, PaymentOut
from .auth import get_current_user, require_role  # (ajusta si el path es distinto)

router = APIRouter(prefix="/facturacion", tags=["facturacion"])

# Crear factura
@router.post("/", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    invoice = Invoice(client_id=payload.client_id, date=payload.date, total=payload.total)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

# Listar facturas (opcional filter: paid)
@router.get("/", response_model=List[InvoiceOut])
def list_invoices(paid: Optional[bool] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(Invoice)
    if paid is not None:
        q = q.filter(Invoice.paid == paid)
    return q.all()

# Obtener factura por id
@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv

# Actualizar factura (marcar pagada, ajustar total)
@router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice(invoice_id: int, payload: InvoiceUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if payload.paid is not None:
        inv.paid = payload.paid
    if payload.total is not None:
        inv.total = payload.total
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

# Registrar pago para una factura
@router.post("/{invoice_id}/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(invoice_id: int, payload: PaymentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    payment = Payment(invoice_id=invoice_id, amount=payload.amount, method=payload.method)
    db.add(payment)
    # opcional: actualizar total pagado / marcar pagado si cubre total
    db.commit()
    db.refresh(payment)

    # actualizar estado invoice si suma pagos >= total
    total_payments = sum(p.amount for p in inv.payments)  # inv.payments puede no actualizarse inmediatamente
    # recalc desde DB
    from sqlalchemy import func
    paid_sum = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(Payment.invoice_id == invoice_id).scalar()
    if paid_sum >= (inv.total or 0):
        inv.paid = True
        db.add(inv)
        db.commit()
        db.refresh(inv)

    return payment

# Listar pagos (por factura o global)
@router.get("/payments", response_model=List[PaymentOut])
def list_payments(invoice_id: Optional[int] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(Payment)
    if invoice_id is not None:
        q = q.filter(Payment.invoice_id == invoice_id)
    return q.all()
