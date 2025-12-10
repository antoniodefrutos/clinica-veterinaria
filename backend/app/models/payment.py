from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ..database import Base

def _now_utc():
    return datetime.now(timezone.utc)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, nullable=True)
    date = Column(DateTime, default=_now_utc)

    invoice = relationship("Invoice", back_populates="payments")
