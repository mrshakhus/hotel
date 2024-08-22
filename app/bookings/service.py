from datetime import date

from app.bookings.dao import BookingConfirmationDAO, BookingDAO
from app.bookings.dependencies import send_confirmation_email_with_link
from app.bookings.enums import ConfirmationAction
from app.bookings.schemas import SBooking


class BookingsService:
    @staticmethod
    async def get_bookings(
        user_id: int
    ) -> list[SBooking]:
        bookings = await BookingDAO.find_all(user_id=user_id)
        return bookings


    @staticmethod
    async def initiate_booking_request(
        room_id: int,
        date_from: date,
        date_to: date,
        user: dict
    ) -> None:
        booking_info = await BookingDAO.get_full_info_by_room_id(room_id)
        booking = await BookingDAO.add(user["id"], room_id, date_from, date_to)
        confirmation_token = await BookingConfirmationDAO.create(
            user["id"], booking["id"],  ConfirmationAction.CREATE
        )

        booking_info["booking_id"] = booking["id"]
        booking_info["user_email"] = user["email"]
        booking_info["date_from"] = date_from
        booking_info["date_to"] = date_to
        booking_info["action"] = ConfirmationAction.CREATE

        await send_confirmation_email_with_link(booking_info, confirmation_token)
        print(confirmation_token)


    @staticmethod
    async def confirm_booking(
        token: str
    ) -> None:
        await BookingConfirmationDAO.confirm(token)
    

    @staticmethod
    async def inititate_booking_cancellation(
        booking_id: int,
        user: dict
    ) -> None:
        booking_info = await BookingDAO.get_full_info_by_booking_id(booking_id)
        confirmation_token = await BookingConfirmationDAO.create(
            user["id"], booking_id, ConfirmationAction.CANCEL)

        booking_info["user_email"] = user["email"]
        booking_info["action"] = ConfirmationAction.CANCEL

        await send_confirmation_email_with_link(booking_info, confirmation_token)
        print(confirmation_token)


    @staticmethod
    async def confirm_booking_cancellation(
        token: str
    ) -> None:
        confirmation = await BookingConfirmationDAO.confirm(token)

        await BookingConfirmationDAO.set_booking_status(
            confirmation, 
            ConfirmationAction.CANCEL
        )
    


    