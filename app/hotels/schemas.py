from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class SHotels(BaseModel):
    id: int = Field(..., gt=0)
    name: str
    location: str
    services: list[str]
    room_quantity: int = Field(..., gt=0)
    image_id: int = Field(..., gt=0)
    rooms_left: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class SHotel(BaseModel):
    id: int = Field(..., gt=0)
    name: str
    location: str
    services: list[str]
    room_quantity: int = Field(..., gt=0)
    image_id: int = Field(..., gt=0)

    model_config = ConfigDict(from_attributes=True)


class SHotelSearchParams(BaseModel):
    location: str
    date_from: date
    date_to: date
    min_price: int = Field(100, gt=0)
    max_price: int = Field(100_000, gt=0)
    hotel_services: list[str] = []

    model_config = ConfigDict(from_attributes=True)