from datetime import date, datetime

from fastapi import APIRouter, Depends
from fastapi_cache import FastAPICache
from fastapi_versioning import version

from app.bookings.dao import BookingConfirmationDAO, BookingDAO
from app.bookings.enums import ConfirmationAction
from app.exceptions import CacheDataExpiredException
from app.bookings.dependencies import get_cache, send_confirmation_email_with_link, set_cache
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/", tags=["На позже"])


@router.post("", status_code=201)
@version(1)
async def initiate_booking_request(
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    booking_info = await BookingDAO.get_full_info_by_room_id(room_id=room_id)

    date_from = date_from.isoformat()
    date_to = date_to.isoformat()

    booking_info["user_email"] = user["email"]
    booking_info["date_from"] = date_from
    booking_info["date_to"] = date_to

    confirmation_token = await BookingConfirmationDAO.create(user["id"], ConfirmationAction.CREATE)
    await send_confirmation_email_with_link(booking_info, confirmation_token)
    print(confirmation_token)

    booking_data = {
        "room_id": room_id,
        "date_from": date_from,
        "date_to": date_to
    }

    cache_key = f"booking:details:{confirmation_token}"
    await set_cache(cache_key, booking_data, expire=900)  # 900 секунд = 15 минут

    return {"message": "Письмо с ссылкой для подтверждения отправлено"}


@router.get("/confirmation/{token}", status_code=200)
@version(1)
async def confirm_booking(
    token: str,
    user: Users = Depends(get_current_user),
):
    await BookingConfirmationDAO.confirm(token)
    
    cache_key = f"booking:details:{token}"
    booking_data = await get_cache(cache_key)
    if not booking_data:
        raise CacheDataExpiredException

    room_id = booking_data["room_id"]
    date_from = datetime.strptime(booking_data["date_from"], "%Y-%m-%d").date()
    date_to = datetime.strptime(booking_data["date_to"], "%Y-%m-%d").date()

    await BookingDAO.add(user.id, room_id, date_from, date_to)
    
    await FastAPICache.clear(key=cache_key)

    return {"message": "Бронирование успешно подтверждено"}