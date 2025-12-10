from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class MedicalHistory(Base):
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, index=True)
    #referencia tanto a client como a pet (permite null por si el evento es genérico)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable = False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    
    event = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    #mantener campos clínicos si ya los tienes o quieres guardar más detalle
    diagnosis = Column(String, nullable=True)
    treatment = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    
    created_by = Column(String, nullable=True)  # nombre del vet/usuario que registró

    client = relationship("Client", back_populates="history")
    pet = relationship("Pet", back_populates="history")
