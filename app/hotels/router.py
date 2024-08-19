import asyncio
from datetime import date, datetime, timezone
import smtplib
from fastapi.encoders import jsonable_encoder
from fastapi_cache.decorator import cache
from fastapi import APIRouter, Query

from app.hotels.dao import HotelDAO
from app.hotels.rooms.schemas import SRooms
from app.hotels.schemas import SHotel, SHotels
from app.tasks.dao import BookingTaskDAO
from app.tasks.email_templates import create_booking_notification_template
from app.config import settings
from app.utils.exception_handlers import validate_dates

router = APIRouter(
    prefix='/hotels',
    tags=['Отели']
)

@router.get("/{location}", status_code=200, response_model=list[SHotels])
@cache(expire=30)
async def get_hotels(
    location: str, 
    date_from: date, 
    date_to: date,
    min_price: int = Query(100, ge=0), 
    max_price: int = Query(100_000, ge=0),
    hotel_services: list[str] = Query([]),  
):
    validate_dates(date_from, date_to)
    
    hotels = await HotelDAO.get_all_hotels(
        location, 
        date_from, 
        date_to,
        min_price,
        max_price,
        hotel_services
    )

    return hotels


@router.get("/{hotel_id}/rooms", status_code=200, response_model=list[SRooms]) 
async def get_rooms(
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
async def get_hotel(
    hotel_id: int
):
    hotel = await HotelDAO.get_hotel(hotel_id)
    return hotel


#for testing:
# @router.get("")
# async def send_notification_1_day_email():
#     """
#     Таска будет напоминать о бронировании тем пользователям, у кого на завтра запланирован заезд в отель. Таска/функция должна выполняться каждый день в 9 утра (задайте через crontab)
#     """
#     todays_date = datetime.now(timezone.utc).date() #get_day_before_users(todays_date)
#     users = await BookingTaskDAO.get_users_for_notification(date(2030,6,5), 1)

#     for user in users:
#         msg_content = create_booking_notification_template(
#             user["email"], 
#             user["date_from"],
#             user["date_to"]
#         )

#         with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
#             server.login(settings.SMTP_USER, settings.SMTP_PASS)
#             server.send_message(msg_content)
