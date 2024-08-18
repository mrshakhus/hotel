from typing import List
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