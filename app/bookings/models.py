from datetime import datetime, timezone
from sqlalchemy import Column, Computed, Date, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Bookings(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    room_id = Column(ForeignKey("rooms.id"))
    user_id = Column(ForeignKey("users.id"))
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    price = Column(Integer, nullable=False)
    total_cost = Column(Integer, Computed("(date_to - date_from) * price"))
    total_days = Column(Integer, Computed("(date_to - date_from)"))

    room = relationship("Rooms", back_populates="booking")
    user = relationship("Users", back_populates="booking")

    def __str__(self) -> str:
        return f"Бронь #{self.id}"
    

class BookingConfirmation(Base):
    __tablename__ = 'booking_confirmations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String, unique=True)
    expires_at = Column(DateTime)
    is_confirmed = Column(Boolean, default=False)

    def is_expired(self):
        return datetime.now(timezone.utc).replace(tzinfo=None) > self.expires_at