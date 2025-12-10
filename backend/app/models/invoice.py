from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date

from ..database import Base

def _now_utc():
    return datetime.now(timezone.utc)

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    total = Column(Float, nullable = False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    paid = Column(Boolean, default=False)

    # relationships
    client = relationship("Client", backref="invoices")
    pet = relationship("Pet", backref="invoices")
    appointment = relationship("Appointment", backref="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
