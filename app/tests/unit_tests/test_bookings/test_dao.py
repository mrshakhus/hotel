from datetime import datetime
from pydantic import TypeAdapter
import pytest
from app.bookings.dao import BookingConfirmationDAO, BookingDAO
from app.bookings.schemas import SBookingConfirmation, SBookingFullInfo
from app.exceptions import ActionAlreadyConfirmedException, IncorrectTokenFortmatException, InvalidDatesException, MoreThan30DaysException, NoBookingToDeleteException, NoRoomFoundException, RoomCanNotBeBooked, ServiceUnavailableException, TokenExpiredException, UserIsNotPresentException


@pytest.mark.parametrize("user_id, room_id, date_from, date_to, expected_exception", [
    (1, 1, "2030-09-01", "2030-09-09", None),
    (1, 1, "2030-09-01", "2030-09-09", None),
    (1, 1, "2030-09-01", "2030-09-09", None),
    (1, 1, "2030-09-01", "2030-09-09", None),
    (1, 20, "2030-09-01", "2030-09-09", NoRoomFoundException),
    (1, 1, "2030-09-01", "2010-08-09", InvalidDatesException),
    (1, 1, "2030-09-01", "2030-10-02", MoreThan30DaysException),
    (100, 1, "2030-09-01", "2030-09-09", ServiceUnavailableException),
    (1, 1, "2030-09-01", "2030-09-09", None),
    (1, 1, "2030-09-01", "2030-09-09", RoomCanNotBeBooked),
])
async def test_add_booking(user_id, room_id, date_from, date_to, expected_exception):
    date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    date_to = datetime.strptime(date_to, "%Y-%m-%d").date()

    if expected_exception:
        with pytest.raises(expected_exception):
            await BookingDAO.add(
                user_id=user_id,
                room_id=room_id,
                date_from=date_from,
                date_to=date_to,
            )
    else:
        booking = await BookingDAO.add(
            user_id=user_id,
            room_id=room_id,
            date_from=date_from,
            date_to=date_to,
        )

        assert booking
        assert booking.user_id == user_id
        assert booking.room_id == room_id
        assert booking.date_from == date_from
        assert booking.date_to == date_to
        assert booking.price > 0
        assert booking.total_cost == (date_to - date_from).days * booking.price
        assert booking.total_days == (date_to - date_from).days


@pytest.mark.parametrize("user_id, booking_id, expected_exception", [
    (1, 1, None),
    (-1, -1, NoBookingToDeleteException),
    (1, 1, NoBookingToDeleteException),
])
async def test_delete_booking(user_id, booking_id, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            await BookingDAO.delete(
                user_id=user_id,
                booking_id=booking_id
            )
    else:
        booking = await BookingDAO.delete(
            user_id=user_id,
            booking_id=booking_id
        )

        assert booking
        assert booking["user_id"] == user_id
        assert booking["id"] == booking_id
        

@pytest.mark.parametrize("room_id, expected_exception", [
    (1, None),
    (1.1, NoRoomFoundException),
    ("1", ServiceUnavailableException),
    (0, NoRoomFoundException),
    (-1, NoRoomFoundException),
    (9999, NoRoomFoundException),
    (None, NoRoomFoundException),
])
async def test_get_full_info(room_id, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            await BookingDAO.get_full_info_by_room_id(
                room_id=room_id
            )
    else:
        booking_full_info = await BookingDAO.get_full_info_by_room_id(
            room_id=room_id
        )

        full_info_adapter = TypeAdapter(SBookingFullInfo)
        validated_full_info = full_info_adapter.validate_python(booking_full_info)
        assert booking_full_info == dict(validated_full_info)


@pytest.mark.parametrize("user_id, expected_exception",[
    (None, UserIsNotPresentException),
    (-999, UserIsNotPresentException), 
    (0, UserIsNotPresentException), 
    (1, None), 
    (999, UserIsNotPresentException)
])
async def test_create_confirmation(user_id, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            await BookingConfirmationDAO.create(user_id)
    else:
        token = await BookingConfirmationDAO.create(user_id)
        print(user_id, token)
        
        assert token
        assert isinstance(token, str)


@pytest.mark.parametrize("token, expected_exception", [
    ("valid_token", None),
    ("invalid_token", IncorrectTokenFortmatException),
    ("expired_token", TokenExpiredException),
    ("confirmed_token", ActionAlreadyConfirmedException),
])
async def test_confirm_booking_dao(token, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            await BookingConfirmationDAO.confirm(token)
    else:
        confirmation = await BookingConfirmationDAO.confirm(token)
        validated_confirmation = SBookingConfirmation.model_validate(confirmation).model_dump()
    
        assert validated_confirmation
        assert confirmation.is_confirmed == True
