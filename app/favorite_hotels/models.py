from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base

class FavoriteHotels(Base):
    __tablename__ = "favorite_hotels"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"))
    hotel_id = Column(ForeignKey("hotels.id"))

    # user = relationship("Users", back_populates="favorite_hotel")
    # hotel = relationship("Hotels", back_populates="favorite_hotel")

