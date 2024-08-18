from pydantic import BaseModel, ConfigDict, Field

class SRooms(BaseModel):
    id: int = Field(..., gt=0)
    hotel_id: int = Field(..., gt=0)
    name: str
    description: str
    price: int = Field(..., ge=0)
    services: list[str]
    quantity: int = Field(..., gt=0)
    image_id: int = Field(..., gt=0)
    total_cost: int = Field(..., ge=0)
    rooms_left: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)