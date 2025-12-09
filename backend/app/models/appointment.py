from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    reason = Column(String)
    veterinarian = Column(String)

    pet_id = Column(Integer, ForeignKey("pets.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))

    completed = Column(Boolean, default=False)

    pet = relationship("Pet")
    client = relationship("Client")
