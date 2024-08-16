from pydantic import BaseModel, ConfigDict

class SRooms(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    price: int
    services: list[str]
    quantity: int
    image_id: int
    total_cost: int
    rooms_left: int

    model_config = ConfigDict(from_attributes=True)