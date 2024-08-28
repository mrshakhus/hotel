from fastapi import APIRouter, Depends

from app.favorite_hotels.service import FavoriteHotelsService
from app.hotels.schemas import SHotel
from app.users.dependencies import get_current_user
from app.users.models import Users


router = APIRouter(
    prefix="/favorites",
    tags=["Избранные отели"]
)


@router.post("", status_code=201)
async def add_to_fovorites(
    hotel_id: int,
    user: Users = Depends(get_current_user)
):
    await FavoriteHotelsService.add_hotel_to_favorites(user["id"], hotel_id)
    return{"message": "Отель добавлен в избранные"}


@router.delete("", status_code=204)
async def delete_from_fovorites(
    favorite_id: int,
    user: Users = Depends(get_current_user)
):
    await FavoriteHotelsService.delete_hotel_from_favorites(favorite_id)


@router.get("", status_code=200, response_model=list[SHotel])
async def get_fovorites(
    user: Users = Depends(get_current_user)
):
    hotels = await FavoriteHotelsService.get_favorite_hotels(user["id"])
    return hotels



