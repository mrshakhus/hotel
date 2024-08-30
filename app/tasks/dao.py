from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from app.bookings.enums import BookingStatus
from app.hotels.rooms.models import Rooms
from app.hotels.models import Hotels
from app.bookings.models import Bookings
from app.database import async_session_maker
from app.users.models import Users
from app.utils.exception_handlers import handle_db_exception, handle_unexpected_exception


class BookingTaskDAO():
    @classmethod
    async def get_users_for_notification(
        cls,
        todays_date: date,
        days_before_check_in: int
    ) -> list[dict]:
        try:
            async with async_session_maker() as session:
                needed_bookings = (
                    select(
                        Bookings.id.label("booking_id"),
                        Bookings.user_id,
                        Users.email.label("user_email"),
                        Bookings.room_id, 
                        Bookings.date_from, 
                        Bookings.date_to
                    )
                    .select_from(Bookings)
                    .join(
                        Users,
                        Users.id == Bookings.user_id
                    )
                    .where(
                        and_(
                            (Bookings.date_from - todays_date) == days_before_check_in,
                            Bookings.status == BookingStatus.ACTIVE
                        )
                    )
                ).cte("needed_bookings")

                booked_room = (
                    select(
                        Rooms.id, 
                        Rooms.hotel_id, 
                        Rooms.name, 
                        Rooms.description, 
                        Rooms.services
                    )
                    .select_from(Rooms)
                    .join(
                        needed_bookings,
                        needed_bookings.c.room_id == Rooms.id
                    )
                ).cte("booked_room")

                booked_hotel = (
                    select(
                        Hotels.id.label("hotel_id"),
                        Hotels.name.label("hotel_name"),
                        Hotels.location,
                    )
                    .select_from(Hotels)
                    .join(
                        booked_room,
                        Hotels.id == booked_room.c.hotel_id,
                    )
                ).cte("booked_hotel")

                get_full_info = (
                    select(
                        booked_room.c.hotel_id, 
                        booked_room.c.name,
                        booked_room.c.description,
                        booked_room.c.services,
                        booked_hotel.c.hotel_name, 
                        booked_hotel.c.location,
                        needed_bookings.c.date_from,
                        needed_bookings.c.date_to,
                        needed_bookings.c.booking_id,
                        needed_bookings.c.user_id,
                        needed_bookings.c.user_email
                    )
                    .select_from(booked_room)
                    .join(
                        booked_hotel,
                        booked_hotel.c.hotel_id == booked_room.c.hotel_id
                    )
                    .join(
                        needed_bookings,
                        needed_bookings.c.room_id == booked_room.c.id
                    )
                    .distinct(needed_bookings.c.booking_id)
                )

                result = await session.execute(get_full_info)
                full_info = result.mappings().all()
                
                return full_info
        
        except (
            SQLAlchemyError, 
            Exception
        ) as e:
            
            extra = {
                "todays_date": todays_date, 
                "days_before_check_in": days_before_check_in
            }

            handle_db_exception(e, extra)
            handle_unexpected_exception(e, extra)


    @classmethod
    async def set_booking_status_expired(
        cls,
        booking_id: int
    ) -> None:
        try:
            async with async_session_maker() as session:
                get_booking = (
                    select(Bookings)
                    .where(Bookings.id == booking_id)
                )
                result = await session.execute(get_booking)
                booking = result.scalars().one()

                booking.status = BookingStatus.EXPIRED
                await session.commit()

        except (
            SQLAlchemyError, 
            Exception
        ) as e:
            
            extra = {
                "booking_id": booking_id
            }

            handle_db_exception(e, extra)
            handle_unexpected_exception(e, extra)