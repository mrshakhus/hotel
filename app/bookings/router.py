from datetime import date, datetime, timezone
import smtplib

from fastapi import APIRouter, Depends, Request
from fastapi_versioning import version

from app.limiter import limiter
from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking, SBookingFullInfo
from app.bookings.service import BookingsService
from app.bookings.dependencies import get_cache, send_confirmation_email_with_link, set_cache
from app.tasks.dao import BookingTaskDAO
from app.tasks.email_templates import create_booking_notification_template
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.config import settings

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирование"]
)


@router.get("", status_code=200, response_model=list[SBooking])
@version(1)
@limiter.limit("1/second")
async def get_bookings(
    request: Request,
    user: Users = Depends(get_current_user)
):
    bookings = await BookingsService.get_bookings(user["id"])
    return bookings


@router.post("", status_code=201)
@version(1)
@limiter.limit("1/second")
async def initiate_booking_request(
    request: Request,
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    await BookingsService.initiate_booking_request(room_id, date_from, date_to, user)
    return {"message": "Письмо с ссылкой для подтверждения отправлено"}


@router.get("/confirmations/{token}", status_code=200)
@version(1)
@limiter.limit("1/second")
async def confirm_booking(
    request: Request,
    token: str,
    user: Users = Depends(get_current_user),
):
    await BookingsService.confirm_booking(token, user)
    return {"message": "Бронирование успешно подтверждено"}


@router.delete("/{booking_id}", status_code=201)
@version(1)
@limiter.limit("1/second")
async def inititate_booking_cancellation(
    request: Request,
    booking_id: int, 
    user: Users = Depends(get_current_user)
):
    await BookingsService.inititate_booking_cancellation(booking_id, user)
    return {"message": "Письмо с ссылкой для подтверждения отправлено"}


@router.get("/cancellation_confirmations/{token}", status_code=200)
@version(1)
@limiter.limit("1/second")
async def confirm_booking_cancellation(
    request: Request,
    token: str,
    user: Users = Depends(get_current_user),
):
    await BookingsService.confirm_booking_cancellation(token)
    return {"message": "Отмена бронирования успешно подтверждена"}


#Для теста
@router.post("/test", status_code=200, response_model=SBookingFullInfo)
@version(1)
@limiter.limit("1/second")
async def test_booking_info(
    request: Request,
    room_id: int
):
    booking_info = await BookingDAO.get_full_info_by_room_id(room_id)
    print(booking_info)

    return booking_info


# # for testing:
# @router.get("")
# @version(1)
# @limiter.limit("1/second")
# async def send_notification_1_and_3_day_email(
#     request: Request
# ):
#     days_before_check_in = 1
#     todays_date = datetime.now(timezone.utc).date()
#     users = await BookingTaskDAO.get_users_for_notification(todays_date, days_before_check_in)

#     if not users:
#         print("NO USERS FOUND FOR NOTIFICATION")
#         return
    
#     for user in users:
#         msg_content = create_booking_notification_template(user, days_before_check_in)

#         with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
#             server.login(settings.SMTP_USER, settings.SMTP_PASS)
#             server.send_message(msg_content)

    
#     days_before_check_in = 3
#     users = await BookingTaskDAO.get_users_for_notification(todays_date, days_before_check_in)

#     if not users:
#         print("NO USERS FOUND FOR NOTIFICATION")
#         return
    
#     for user in users:
#         msg_content = create_booking_notification_template(user, days_before_check_in)

#         with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
#             server.login(settings.SMTP_USER, settings.SMTP_PASS)
#             server.send_message(msg_content)


# # for testing:
# @router.get("")
# @version(1)
# @limiter.limit("1/second")
# async def send_notification_1_and_3_day_email(
#     request: Request
# ):
#     pass