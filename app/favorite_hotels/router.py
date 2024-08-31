from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.favorite_hotels.service import FavoriteHotelsService
from app.hotels.schemas import SHotel
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.limiter import limiter


router = APIRouter(
    prefix="/favorites",
    tags=["Избранные отели"]
)


@router.post("", status_code=201)
@version(1)
@limiter.limit("1/second")
async def add_to_fovorites(
    request: Request,
    hotel_id: int,
    user: Users = Depends(get_current_user)
):
    await FavoriteHotelsService.add_hotel_to_favorites(user["id"], hotel_id)
    return{"message": "Отель добавлен в избранные"}


@router.delete("", status_code=204)
@version(1)
@limiter.limit("1/second")
async def delete_from_fovorites(
    request: Request,
    favorite_id: int,
    user: Users = Depends(get_current_user)
):
    await FavoriteHotelsService.delete_hotel_from_favorites(favorite_id)


@router.get("", status_code=200, response_model=list[SHotel])
@version(1)
@limiter.limit("1/second")
async def get_fovorites(
    request: Request,
    user: Users = Depends(get_current_user)
):
    hotels = await FavoriteHotelsService.get_favorite_hotels(user["id"])
    return hotels