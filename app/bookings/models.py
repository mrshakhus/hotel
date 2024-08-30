from datetime import datetime, timezone
from sqlalchemy import Column, Computed, Date, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.bookings.enums import BookingStatus, BookingAction
from app.database import Base

class Bookings(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    room_id = Column(ForeignKey("rooms.id"))
    user_id = Column(ForeignKey("users.id"))
    status = Column(Integer, nullable=False, default=BookingStatus.PENDING)
    created_at = Column(DateTime, nullable=False,  default=datetime.now(timezone.utc).replace(tzinfo=None))
    cancelled_at = Column(DateTime)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    price = Column(Integer, nullable=False)
    total_cost = Column(Integer, Computed("(date_to - date_from) * price"))
    total_days = Column(Integer, Computed("(date_to - date_from)"))

    room = relationship("Rooms", back_populates="booking")
    user = relationship("Users", back_populates="booking")
    booking_confirmation = relationship("BookingConfirmations", back_populates="booking")

    def __str__(self) -> str:
        return f"Бронь #{self.id}"
    

class BookingConfirmations(Base):
    __tablename__ = 'booking_confirmations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    action = Column(Integer, nullable=False, default=BookingAction.CONFIRM)
    token = Column(String, unique=True)
    expires_at = Column(DateTime, nullable=False)
    is_confirmed = Column(Boolean, default=False)

    user = relationship("Users", back_populates="booking_confirmation")
    booking = relationship("Bookings", back_populates="booking_confirmation")

    def is_expired(self):
        return datetime.now(timezone.utc).replace(tzinfo=None) > self.expires_at