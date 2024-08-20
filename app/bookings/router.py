from datetime import date, datetime

from fastapi import APIRouter, Depends
from fastapi_cache import FastAPICache
from fastapi_versioning import version

from app.bookings.dao import BookingConfirmationDAO, BookingDAO
from app.bookings.enums import ConfirmationAction
from app.bookings.schemas import SBooking
from app.exceptions import CacheDataExpiredException
from app.bookings.dependencies import get_cache, send_confirmation_email_with_link, set_cache
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get("", status_code=200, response_model=list[SBooking])
@version(1)
async def get_bookings(
    user: Users = Depends(get_current_user)
):
    return await BookingDAO.find_all(user_id=user["id"])


@router.post("", status_code=201)
@version(1)
async def initiate_booking_request(
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    booking_info = await BookingDAO.get_full_info_by_room_id(room_id)
    booking = await BookingDAO.add(user["id"], room_id, date_from, date_to)
    confirmation_token = await BookingConfirmationDAO.create(
        user["id"], booking["id"],  ConfirmationAction.CREATE)

    booking_info["booking_id"] = booking["id"]
    booking_info["user_email"] = user["email"]
    booking_info["date_from"] = date_from
    booking_info["date_to"] = date_to
    booking_info["action"] = ConfirmationAction.CREATE

    await send_confirmation_email_with_link(booking_info, confirmation_token)
    print(confirmation_token)

    return {"message": "Письмо с ссылкой для подтверждения отправлено"}


@router.get("/confirmations/{token}", status_code=200)
@version(1)
async def confirm_booking(
    token: str,
    user: Users = Depends(get_current_user),
):
    await BookingConfirmationDAO.confirm(token)

    return {"message": "Бронирование успешно подтверждено"}


@router.delete("/{booking_id}", status_code=201)
@version(1)
async def inititate_booking_deletion(
    booking_id: int, 
    user: Users = Depends(get_current_user)
):
    booking_info = await BookingDAO.get_full_info_by_booking_id(booking_id)
    confirmation_token = await BookingConfirmationDAO.create(
        user["id"], booking_id, ConfirmationAction.CANCEL)

    booking_info["user_email"] = user["email"]
    booking_info["action"] = ConfirmationAction.CANCEL

    await send_confirmation_email_with_link(booking_info, confirmation_token)
    print(confirmation_token)

    return {"message": "Письмо с ссылкой для подтверждения отправлено"}


@router.get("/cancellation_confirmation/{token}", status_code=200)
@version(1)
async def confirm_booking(
    token: str,
    user: Users = Depends(get_current_user),
):
    confirmation = await BookingConfirmationDAO.confirm(token)

    await BookingConfirmationDAO.set_booking_status(
        confirmation, 
        ConfirmationAction.CANCEL
    )

    return {"message": "Отмена бронирования успешно подтверждена"}


#Для теста
@router.post("/test", status_code=200)
@version(1)
async def test_booking_info(
    room_id: int
):
    booking_info = await BookingDAO.get_full_info_by_room_id(room_id)

    return booking_info