from datetime import datetime
from pydantic import TypeAdapter
import pytest
from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBookingFullInfo
from app.exceptions import InvalidDatesException, MoreThan30DaysException, NoBookingToDeleteException, NoRoomFoundException, RoomCanNotBeBooked, ServiceUnavailableException


# @pytest.mark.parametrize("user_id, room_id, date_from, date_to, expected_exception", [
#     (1, 1, "2030-09-01", "2030-09-09", None),
#     (1, 1, "2030-09-01", "2030-09-09", None),
#     (1, 1, "2030-09-01", "2030-09-09", None),
#     (1, 1, "2030-09-01", "2030-09-09", None),
#     (1, 20, "2030-09-01", "2030-09-09", NoRoomFoundException),
#     (1, 1, "2030-09-01", "2010-08-09", InvalidDatesException),
#     (1, 1, "2030-09-01", "2030-10-02", MoreThan30DaysException),
#     (100, 1, "2030-09-01", "2030-09-09", ServiceUnavailableException),
#     (1, 1, "2030-09-01", "2030-09-09", None),
#     (1, 1, "2030-09-01", "2030-09-09", RoomCanNotBeBooked),
# ])
# async def test_add_booking(user_id, room_id, date_from, date_to, expected_exception):
#     date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
#     date_to = datetime.strptime(date_to, "%Y-%m-%d").date()

#     if expected_exception:
#         with pytest.raises(expected_exception):
#             await BookingDAO.add(
#                 user_id=user_id,
#                 room_id=room_id,
#                 date_from=date_from,
#                 date_to=date_to,
#             )
#     else:
#         booking = await BookingDAO.add(
#             user_id=user_id,
#             room_id=room_id,
#             date_from=date_from,
#             date_to=date_to,
#         )
    
#         assert booking
#         assert booking.user_id == user_id
#         assert booking.room_id == room_id
#         assert booking.date_from == date_from
#         assert booking.date_to == date_to
#         assert booking.price > 0
#         assert booking.total_cost == (date_to - date_from).days * booking.price
#         assert booking.total_days == (date_to - date_from).days


# @pytest.mark.parametrize("user_id, booking_id, expected_exception", [
#     (1, 1, None),
#     (-1, -1, NoBookingToDeleteException),
#     (1, 1, NoBookingToDeleteException),
# ])
# async def test_delete_booking(user_id, booking_id, expected_exception):
#     if expected_exception:
#         with pytest.raises(expected_exception):
#             await BookingDAO.delete(
#                 user_id=user_id,
#                 booking_id=booking_id
#             )
#     else:
#         booking = await BookingDAO.delete(
#             user_id=user_id,
#             booking_id=booking_id
#         )

#         assert booking
#         assert booking["user_id"] == user_id
#         assert booking["id"] == booking_id
        
@pytest.mark.parametrize("room_id, expected_exception", [
    ()
])
async def test_get_full_info(room_id, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            await BookingDAO.get_full_info(
                room_id=room_id
            )
    else:
        booking_full_info = await BookingDAO.get_full_info(
            room_id=room_id
        )

        full_info_adapter = TypeAdapter(SBookingFullInfo) #Валидировать данные?
        full_info_adapter.validate_python(booking_full_info)

        assert booking_full_info
        assert booking_full_info.hotel_id > 0
        assert booking_full_info.name
        assert booking_full_info.description
        assert booking_full_info.services
        assert booking_full_info.hotel_name
        assert booking_full_info.location
