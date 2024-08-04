from datetime import date

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from pydantic import TypeAdapter

from app.bookings.dao import BookingConfirmationDAO, BookingDAO
from app.bookings.schemas import SBooking
from app.config import settings
from app.exceptions import IncorrectOrAbcentToken, RoomCanNotBeBooked
from app.tasks.tasks import send_booking_confirmation_email, send_confirmation_email_with_link
from app.users.dependencies import get_current_user
from app.bookings.dependencies import get_confirmation_token
from app.users.models import Users

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get("", response_model=list[SBooking])
@version(1)
async def get_bookings(user: Users = Depends(get_current_user)):
    return await BookingDAO.find_all(user_id=user.id)


@router.delete("/{booking_id}", status_code=204)
@version(1)
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    await BookingDAO.delete(user.id, booking_id)


@router.post("/confirmation", status_code=200)
@version(1)
async def start_confirmation(
    user: Users = Depends(get_current_user),
    token: str = Depends(get_confirmation_token),
    ):
    await send_confirmation_email_with_link(user.email, token)
    return {"message": "Ссылка успешно отправлена на эл. почту"}


@router.get("/confirmation/{token}", status_code=200)
@version(1)
async def confirm_booking(token: str):
    confirmation = await BookingConfirmationDAO.confirm(token)
    if not confirmation:
        raise IncorrectOrAbcentToken
    return {"message": "Бронирование успешно подтверждено"}


@router.post("", status_code=200)
@version(1)
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    token: str = Depends(get_confirmation_token),
    user: Users = Depends(get_current_user),
):
    confirmation = await BookingConfirmationDAO.confirm(token)
    if not confirmation:
        booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
        if not booking:
            raise RoomCanNotBeBooked
        
        # bookings_adapter = TypeAdapter(SBooking)
        # bookings_dict = bookings_adapter.validate_python(booking).model_dump()
        # send_booking_confirmation_email(bookings_dict, settings.SMTP_USER)
        
        return booking