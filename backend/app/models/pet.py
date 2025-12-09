from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    species = Column(String)
    breed = Column(String)
    age = Column(Integer)
    weight = Column(Integer)

    owner_id = Column(Integer, ForeignKey("clients.id"))
    owner = relationship("Client", backref="pets")
