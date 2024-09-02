from datetime import date
from fastapi_cache.decorator import cache
from fastapi import APIRouter, Query, Request
from fastapi_versioning import version
from app.limiter import limiter

from app.hotels.dao import HotelDAO
from app.hotels.rooms.schemas import SRoomsInfo
from app.hotels.schemas import SHotel, SHotels
from app.hotels.service import HotelsService
from app.utils.exception_handlers import validate_dates

router = APIRouter(
    prefix='/hotels',
    tags=['Отели']
)

@router.get("/{location}", status_code=200, response_model=list[SHotels])
@version(1)
@cache(expire=30)
@limiter.limit("1/second")
async def get_hotels(
    request: Request,
    location: str,
    date_from: date,
    date_to: date,
    min_price: int = Query(100, ge=0), 
    max_price: int = Query(100_000, ge=0),
    hotel_services: list[str] = Query([])
):
    validate_dates(date_from, date_to)
    
    hotels = await HotelsService.get_hotels(
        location, 
        date_from, 
        date_to,
        min_price,
        max_price,
        hotel_services
    )

    return hotels


@router.get("/{hotel_id}/rooms", status_code=200, response_model=list[SRoomsInfo])
@version(1)
@limiter.limit("1/second") 
async def get_rooms(
    request: Request,
    hotel_id: int, 
    date_from: date, 
    date_to: date,
    room_services: list[str] = Query([])

):
    validate_dates(date_from, date_to)

    rooms = await HotelDAO.get_all_rooms(
        hotel_id,
        date_from, 
        date_to,
        room_services
    )

    return rooms


@router.get("/id/{hotel_id}", status_code=200, response_model=SHotel)
@version(1)
@limiter.limit("1/second")
async def get_hotel(
    request: Request,
    hotel_id: int
):
    hotel = await HotelDAO.get_hotel(hotel_id)
    return hotel