from sqlalchemy import JSON, Column, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import relationship
from app.database import Base
from app.favorite_hotels.models import FavoriteHotels 

class Hotels(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    tsvector = Column(TSVECTOR, nullable=False)
    services = Column(JSONB)
    room_quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)

    room = relationship("Rooms", back_populates="hotel")
    favorite_hotel = relationship("FavoriteHotels", back_populates="hotel")

    def __str__(self) -> str:
        return f"{self.name}"

# @listens_for(Hotels, 'before_insert')
# def generate_tsvector_before_insert(mapper, connection, target):
#     target.tsvector = func.to_tsvector('russian', target.location)

# @listens_for(Hotels, 'before_update')
# def generate_tsvector_before_update(mapper, connection, target):
#     target.tsvector = func.to_tsvector('russian', target.location)

