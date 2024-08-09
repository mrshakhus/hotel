from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class SBooking(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int

    model_config = ConfigDict(from_attributes=True)

class SBookingConfirmation(BaseModel):
    id: int
    user_id: int
    token: str
    expires_at: datetime
    is_confirmed: bool

    model_config = ConfigDict(from_attributes=True)

class SBookingFullInfo(BaseModel):
    hotel_id: int = Field(..., ge=0)
    name: str
    description: str
    services: list[str]
    hotel_name: str
    location: str

    model_config = ConfigDict(from_attributes=True)