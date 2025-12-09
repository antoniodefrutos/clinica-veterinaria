from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from ..database import get_db
from ..models.invoice import Invoice
from ..schemas.informes import IncomeReport
from ..utils.security import require_admin  # Asegúrate de que existe, si no usa get_current_user

router = APIRouter(prefix="/informes", tags=["informes"])


@router.get("/ingresos", response_model=IncomeReport)
def informe_ingresos(
    fecha_inicio: date = Query(..., description="Fecha inicio en formato AAAA-MM-DD"),
    fecha_fin: date = Query(..., description="Fecha fin en formato AAAA-MM-DD"),
    db: Session = Depends(get_db),
    _=Depends(require_admin),  # restringido a admins; si quieres quitarlo, elimina esta línea
):
    """
    Devuelve:
    - total de ingresos entre dos fechas
    - número total de facturas en ese rango
    """

    # Validación del rango
    if fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=400,
            detail="La fecha de inicio no puede ser mayor que la fecha fin."
        )

    # Consulta agregada
    resultado = (
        db.query(
            func.coalesce(func.sum(Invoice.total), 0).label("total"),
            func.count(Invoice.id).label("num_facturas"),
        )
        .filter(Invoice.date >= fecha_inicio)
        .filter(Invoice.date <= fecha_fin)
        .one()
    )

    return IncomeReport(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        total=float(resultado.total),
        num_facturas=int(resultado.num_facturas),
    )