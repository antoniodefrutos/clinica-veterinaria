# backend/app/models/billing.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    date = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, default=0.0)
    paid = Column(Boolean, default=False)

    client = relationship("Client")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    method = Column(String)

    invoice = relationship("Invoice", backref="payments")
