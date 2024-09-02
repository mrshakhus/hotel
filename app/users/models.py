import enum
from sqlalchemy import Column, DateTime, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
from app.users.enums import UserRole


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    # role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.USER)    
    hashed_password = Column(String, nullable=False)
    password_changed_at = Column(DateTime)

    booking = relationship("Bookings", back_populates="user")
    booking_confirmation = relationship("BookingConfirmations", back_populates="user")
    favorite_hotel = relationship("FavoriteHotels", back_populates="user")

    def __str__(self) -> str:
        return f"Пользователь {self.email}"
    
