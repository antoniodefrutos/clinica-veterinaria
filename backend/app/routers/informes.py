from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict, Any

from ..database import get_db
from ..models.invoice import Invoice
from ..utils.security import get_current_user

router = APIRouter(prefix="/informes", tags=["informes"])

@router.get("/ingresos")
def get_ingresos(fecha_inicio: str, fecha_fin: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    fecha_inicio, fecha_fin: ISO dates YYYY-MM-DD
    Returns:
      - total: float
      - invoices_count: int
      - num_facturas: int (same as invoices_count)
      - invoices: list of invoices (id, date, total)
      - monthly: [{month: 'YYYY-MM', total: float}]
    """
    try:
        inicio = datetime.fromisoformat(fecha_inicio)
        fin = datetime.fromisoformat(fecha_fin)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")
    q = db.query(Invoice).filter(Invoice.date >= inicio.date(), Invoice.date <= fin.date())
    total = float(q.with_entities(func.coalesce(func.sum(Invoice.total), 0)).scalar() or 0.0)
    count = q.count()
    invoices = [
        {"id": inv.id, "date": inv.date.isoformat() if inv.date else None, "total": float(inv.total)}
        for inv in q.order_by(Invoice.date).all()
    ]

    # monthly aggregation
    monthly_q = db.query(
        func.strftime('%Y-%m', Invoice.date).label('month'),
        func.coalesce(func.sum(Invoice.total), 0).label('sum')
    ).filter(Invoice.date >= inicio.date(), Invoice.date <= fin.date()).group_by('month').order_by('month')
    monthly = [{"month": r.month, "total": float(r.sum)} for r in monthly_q.all()]

    return {
        "fecha_inicio": inicio.date().isoformat(),
        "fecha_fin": fin.date().isoformat(),
        "total": total,
        "invoices_count": count,
        "num_facturas": count,
        "invoices": invoices,
        "monthly": monthly,
    }