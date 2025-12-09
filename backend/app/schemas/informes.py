from pydantic import BaseModel
from datetime import date

class IncomeReport(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    total: float
    num_facturas: int
