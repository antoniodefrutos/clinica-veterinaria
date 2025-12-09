# backend/app/models/invoice.py
from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ..database import Base

def _now_utc():
    return datetime.now(timezone.utc)

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)

    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=_now_utc)
    paid = Column(Boolean, default=False)

    # relationships
    client = relationship("Client", backref="invoices")
    pet = relationship("Pet", backref="invoices")
    appointment = relationship("Appointment", backref="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
