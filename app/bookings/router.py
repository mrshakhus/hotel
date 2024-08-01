from datetime import date

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from pydantic import TypeAdapter

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.config import settings
from app.exceptions import RoomCanNotBeBooked
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get("", response_model=list[SBooking])
@version(1)
async def get_bookings(user: Users = Depends(get_current_user)):
    return await BookingDAO.find_all(user_id=user.id)


@router.post("", status_code=200)
@version(1)
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCanNotBeBooked

    bookings_adapter = TypeAdapter(SBooking)
    bookings_dict = bookings_adapter.validate_python(booking).model_dump()

    # send_booking_confirmation_email(bookings_dict, settings.SMTP_USER)
    return booking


@router.delete("/{booking_id}", status_code=204)
@version(1)
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    await BookingDAO.delete(user.id, booking_id)
