from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SBooking(BaseModel):
    id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    status: int
    created_at: datetime
    cancelled_at: Optional[datetime]
    date_from: date
    date_to: date
    price: int = Field(..., ge=0)
    total_cost: int = Field(..., ge=0)
    total_days: int = Field(..., gt=0)

    model_config = ConfigDict(from_attributes=True)


class SBookingConfirmation(BaseModel):
    id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    booking_id: int = Field(..., gt=0)
    action: int
    token: str
    expires_at: datetime
    is_confirmed: bool

    model_config = ConfigDict(from_attributes=True)


class SBookingFullInfo(BaseModel):
    hotel_id: int = Field(..., gt=0)
    name: str
    description: str
    services: list[str]
    hotel_name: str
    location: str

    model_config = ConfigDict(from_attributes=True)