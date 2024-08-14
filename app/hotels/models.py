from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Hotels(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    services = Column(JSONB)
    room_quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)

    room = relationship("Rooms", back_populates="hotel")

    def __str__(self) -> str:
        return f"{self.name}"
