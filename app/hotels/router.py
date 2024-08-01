import asyncio
from datetime import date, datetime, timezone
import smtplib
from fastapi_cache.decorator import cache
from fastapi import APIRouter
from pydantic import EmailStr, TypeAdapter

from app.exceptions import MoreThan30DaysException, WrongDatesException
from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotels
from app.tasks.dao import BookingTaskDAO
from app.tasks.email_templates import create_booking_notification_template
from app.config import settings


router = APIRouter(
    prefix='/hotels',
    tags=['Отели']
)

@router.get("/{location}", status_code=200) #TO DO new schema HotelInfo
@cache(expire=30)
async def get_hotels(location: str, date_from: date, date_to: date):
    if date_from >= date_to:
        raise WrongDatesException
    elif (date_to - date_from).days > 30:
        raise MoreThan30DaysException
    
    hotels = await HotelDAO.get_all_hotels(location, date_from, date_to)
    hotels_adapter = TypeAdapter(list[SHotels])
    hotels_json = hotels_adapter.validate_python(hotels)
    return hotels_json


@router.get("/{hotel_id}/rooms", status_code=200) # Ideally should validate data
async def get_rooms(hotel_id: int, date_from: date, date_to: date):
    rooms = await HotelDAO.get_all_rooms(hotel_id, date_from, date_to)

    return rooms


@router.get("/id/{hotel_id}", status_code=200)
async def get_hotel(hotel_id: int):
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
