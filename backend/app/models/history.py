from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class MedicalHistory(Base):
    __tablename__ = "medical_histories"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    diagnosis = Column(String, nullable=True)
    treatment = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    created_by = Column(String, nullable=True)  # nombre del vet/usuario que registró

    pet = relationship("Pet", backref="medical_histories")
