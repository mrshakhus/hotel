from datetime import datetime

from httpx import AsyncClient
import pytest
from app.bookings.dao import BookingDAO

@pytest.mark.parametrize(
    "authenticated_ac",
    [
        {"email": "test@test.com", "password": "test"},
    ],
    indirect=True
)
async def test_add_and_get_booking(authenticated_ac: AsyncClient):
    new_booking = await BookingDAO.add_booking(
        user_id = 2,
        room_id = 2,
        date_from = datetime.strptime("2023-07-05", "%Y-%m-%d"),
        date_to = datetime.strptime("2023-07-25", "%Y-%m-%d"),
    )

    assert new_booking.room_id == 2
    assert new_booking.user_id == 2

    print(new_booking)

    booking = await BookingDAO.find_one_or_none(id=new_booking.id)

    assert booking is not None

