from datetime import date, datetime

from fastapi import APIRouter, Depends
from fastapi_versioning import version

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking, SBookingFullInfo
from app.bookings.service import BookingsService
from app.bookings.dependencies import get_cache, send_confirmation_email_with_link, set_cache
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирование"]
)


@router.get("", status_code=200, response_model=list[SBooking])
@version(1)
async def get_bookings(
    user: Users = Depends(get_current_user)
):
    bookings = await BookingsService.get_bookings(user["id"])
    return bookings


@router.post("", status_code=201)
@version(1)
async def initiate_booking_request(
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    await BookingsService.initiate_booking_request(room_id, date_from, date_to, user)
    return {"message": "Письмо с ссылкой для подтверждения отправлено"}


@router.get("/confirmations/{token}", status_code=200)
@version(1)
async def confirm_booking_cancellation(
    token: str,
    user: Users = Depends(get_current_user),
):
    await BookingsService.confirm_booking(token)
    return {"message": "Бронирование успешно подтверждено"}


@router.delete("/{booking_id}", status_code=201)
@version(1)
async def inititate_booking_cancellation(
    booking_id: int, 
    user: Users = Depends(get_current_user)
):
    await BookingsService.inititate_booking_cancellation(booking_id, user)
    return {"message": "Письмо с ссылкой для подтверждения отправлено"}


@router.get("/cancellation_confirmations/{token}", status_code=200)
@version(1)
async def confirm_booking_cancellation(
    token: str,
    user: Users = Depends(get_current_user),
):
    await BookingsService.confirm_booking_cancellation(token)
    return {"message": "Отмена бронирования успешно подтверждена"}


#Для теста
@router.post("/test", status_code=200, response_model=SBookingFullInfo)
@version(1)
async def test_booking_info(
    room_id: int
):
    booking_info = await BookingDAO.get_full_info_by_room_id(room_id)
    print(booking_info)

    return booking_info
