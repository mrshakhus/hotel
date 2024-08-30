from datetime import date

from fastapi_cache import FastAPICache

from app.logger import logger
from app.bookings.dao import BookingConfirmationDAO, BookingDAO
from app.bookings.dependencies import get_cache, set_cache
from app.bookings.enums import BookingAction
from app.bookings.schemas import SBooking
from celery.result import AsyncResult
from app.exceptions import BookingAPIException
from app.tasks.tasks import send_confirmation_email_with_link, set_booking_status_expired
from app.utils.exception_handlers import handle_exception, handle_unexpected_exception


class BookingsService:
    @staticmethod
    async def get_bookings(
        user_id: int
    ) -> list[dict]:
        try:
            bookings = await BookingDAO.find_all(user_id=user_id)
            return bookings
        
        except(
            BookingAPIException,
            Exception
        ) as e:
            
            extra = {
                "user_id": user_id
            }

            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)


    @staticmethod
    async def initiate_booking_request(
        room_id: int,
        date_from: date,
        date_to: date,
        user: dict
    ) -> None:
        try:
            booking_info = await BookingDAO.get_full_info_by_room_id(room_id)
            booking = await BookingDAO.add(user["id"], room_id, date_from, date_to)
            confirmation_token = await BookingConfirmationDAO.create(
                user["id"], booking["id"],  BookingAction.CONFIRM
            )

            booking_info["booking_id"] = booking["id"]
            booking_info["user_email"] = user["email"]
            booking_info["date_from"] = date_from
            booking_info["date_to"] = date_to
            booking_info["action"] = BookingAction.CONFIRM

            send_confirmation_email_with_link.delay(booking_info, confirmation_token)
            print(confirmation_token)

            expire_task = set_booking_status_expired.apply_async(
                (booking["id"],), countdown=60)
            logger.info(msg="TASK CREATED")

            cache_key = f"celery_task:details:{user["email"]}"
            print(cache_key)
            await set_cache(cache_key, expire_task.id, expire=60)
            logger.info(msg="CACHE SETTED")

        except(
            BookingAPIException,
            Exception
        ) as e:
            
            extra = {
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
                "user": user
            }

            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)


    @staticmethod
    async def confirm_booking(
        token: str,
        user: dict
    ) -> None:
        try:
            confirmation = await BookingConfirmationDAO.confirm(token)

            await BookingConfirmationDAO.set_booking_status(
                confirmation, 
                BookingAction.CONFIRM
            )

            cache_key = f"celery_task:details:{user["email"]}"
            task_id = await get_cache(cache_key)
            await FastAPICache.clear(key=cache_key)
            logger.info(msg="CACHE CLEARED")
            
            expire_task = AsyncResult(task_id)
            expire_task.revoke(terminate=True)
            logger.info(msg="TASK TERMINATED")
        
        except(
            BookingAPIException,
            Exception
        ) as e:
            
            extra = {
                "token": token,
                "user": user
            }

            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)
        
    

    @staticmethod
    async def inititate_booking_cancellation(
        booking_id: int,
        user: dict
    ) -> None:
        try:
            booking_info = await BookingDAO.get_full_info_by_booking_id(booking_id)
            confirmation_token = await BookingConfirmationDAO.create(
                user["id"], booking_id, BookingAction.CANCEL)

            booking_info["user_email"] = user["email"]
            booking_info["action"] = BookingAction.CANCEL

            send_confirmation_email_with_link.delay(booking_info, confirmation_token)
            print(confirmation_token)

        except(
            BookingAPIException,
            Exception
        ) as e:
            
            extra = {
                "booking_id": booking_id,
                "user": user
            }

            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)


    @staticmethod
    async def confirm_booking_cancellation(
        token: str
    ) -> None:
        try:
            confirmation = await BookingConfirmationDAO.confirm(token)

            await BookingConfirmationDAO.set_booking_status(
                confirmation, 
                BookingAction.CANCEL
            )

        except(
            BookingAPIException,
            Exception
        ) as e:
            
            extra = {
                "token": token
            }

            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)
    


    