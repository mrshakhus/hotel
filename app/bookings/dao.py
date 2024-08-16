from datetime import date, datetime, timedelta, timezone
import secrets
from sqlalchemy.exc import IntegrityError

from sqlalchemy import and_, delete, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError
from app.bookings.models import Bookings, BookingConfirmations
from app.dao.base import BaseDAO
from app.utils.exception_handlers import handle_db_exception, handle_exception, validate_dates
from app.exceptions import BookingAlreadyConfirmedException, IncorrectTokenFortmatException, NoBookingToDeleteException, NoRoomFoundException, RoomCanNotBeBooked, TokenExpiredException, UserIsNotPresentException
from app.hotels.models import Hotels
from app.logger import logger

from app.database import async_session_maker, engine
from app.hotels.rooms.models import Rooms


class BookingDAO(BaseDAO):
    model = Bookings
    
    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        validate_dates(date_from, date_to)
        try:
            async with async_session_maker() as session:
                """
                WITH booked_rooms AS(
                SELECT * FROM bookings
                WHERE room_id = 1 AND
                (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                (date_from <= '2023-05-15' AND date_to > '2023-05-15')
                )
                """
                booked_rooms = select(Bookings).where(
                    and_(
                        Bookings.room_id == room_id,
                        or_(
                            and_(
                                Bookings.date_from >= date_from,
                                Bookings.date_from <= date_to
                            ),
                            and_(
                                Bookings.date_from <= date_from,
                                Bookings.date_to > date_from
                            )
                        )
                    )
                ).cte("booked_rooms")

                """
                SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms 
                LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
                WHERE rooms.id = 1
                GROUP BY rooms.quantity, booked_rooms.room_id
                """
                get_rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id)
                        .filter(booked_rooms.c.room_id.is_not(None))
                        .label("rooms_left"))
                    )
                    .select_from(Rooms)
                    .join(
                        booked_rooms,
                        booked_rooms.c.room_id == Rooms.id,
                        isouter=True
                    )
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )

                # print(get_rooms_left.compile(engine, compile_kwargs = {"literal_binds": True}))
                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()
                if not isinstance(rooms_left, int):
                    raise NoRoomFoundException
                

                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()

                    add_new_booking = (
                        insert(Bookings).values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        ).returning(
                            Bookings
                        )
                    )
                    booking = await session.execute(add_new_booking)
                    await session.commit()
                    result = booking.mappings().one()["Bookings"]
                    return result
                else:
                    raise RoomCanNotBeBooked
                
        except (
            SQLAlchemyError, 
            NoRoomFoundException, 
            RoomCanNotBeBooked, 
            Exception,
            ) as e:

            extra = { 
                "user_id": user_id, 
                "room_id": room_id, 
                "date_from": date_from, 
                "date_to": date_to
            }

            handle_exception(e, NoRoomFoundException, extra)
            handle_exception(e, RoomCanNotBeBooked, extra)

            handle_db_exception(e, extra)


    @classmethod
    async def delete(
        cls,
        user_id: int,
        booking_id: int,
    ):
        try:
            async with async_session_maker() as session:
                delete_booking = (
                    delete(Bookings)
                    .filter_by(id=booking_id, user_id=user_id)
                    .returning(Bookings)
                )
                result = await session.execute(delete_booking)
                booking = result.mappings().all()

                if not booking:
                    raise NoBookingToDeleteException
                
                await session.commit()
                return booking[0]["Bookings"]
            
        except (
            SQLAlchemyError, 
            NoBookingToDeleteException, 
            Exception
            ) as e:
            extra = { 
                "user_id": user_id, 
                "booking_id": booking_id
            }
            
            msg="Booking not found for deletion"
            handle_exception(e, NoBookingToDeleteException, extra, msg)

            handle_db_exception(e, extra)

    
    @classmethod
    async def get_full_info(
        cls,
        room_id: int
        ):
        try:
            async with async_session_maker() as session:
                """
                WITH booked_room AS(
                    SELECT hotel_id, name, description, services 
                    FROM rooms
                    WHERE rooms.id = 1
                ),
                """
                booked_room = (
                    select(Rooms.hotel_id, Rooms.name, Rooms.description, Rooms.services)
                    .where(Rooms.id == room_id)
                ).cte("booked_room")

                """
                booked_hotel AS(
                    SELECT hotels.name
                    AS "hotel_name"
                    , hotels.location 
                    FROM hotels
                    JOIN booked_room
                    ON hotels.id = booked_room.hotel_id
                )
                """
                booked_hotel = (
                    select(
                        Hotels.id.label("hotel_id"),
                        Hotels.name.label("hotel_name"),
                        Hotels.location
                    )
                    .select_from(Hotels)
                    .join(
                        booked_room,
                        Hotels.id == booked_room.c.hotel_id,
                    )
                ).cte("booked_hotel")

                """
                SELECT * FROM booked_room, booked_hotel
                """
                get_full_info = (
                    select(booked_room, booked_hotel.c.hotel_name, booked_hotel.c.location)
                    .select_from(booked_room)
                    .join(
                        booked_hotel,
                        booked_hotel.c.hotel_id == booked_room.c.hotel_id
                    )
                )

                result = await session.execute(get_full_info)
                full_info = result.mappings().all()

                if not full_info:
                    raise NoRoomFoundException

                return dict(full_info[0])
            
        except (
            SQLAlchemyError, 
            NoRoomFoundException, 
            Exception
            ) as e:

            extra = { 
                "room_id": room_id
            }

            handle_exception(e, NoRoomFoundException, extra)

            handle_db_exception(e, extra)




class BookingConfirmationDAO(BaseDAO):
    model = BookingConfirmations

    @classmethod
    async def create(
        cls, 
        user_id: int
    ):
        try:
            token = secrets.token_urlsafe()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
            confirmation = {
                    "user_id": user_id,
                    "token": token,
                    "expires_at": expires_at.replace(tzinfo=None)
                }
            
            async with async_session_maker() as session:
                add_confimation = (
                    insert(BookingConfirmations)
                    .values(confirmation)
                )
                await session.execute(add_confimation)
                await session.commit()
                return token
        
        except (
            SQLAlchemyError, 
            IntegrityError, 
            Exception
        ) as e:
            extra = { 
                "user_id": user_id
            }

            if isinstance(e, IntegrityError):
                msg="No user was found"
                logger.error(msg, extra=extra, exc_info=True)
                raise UserIsNotPresentException

            handle_db_exception(e, extra)
            

    @classmethod
    async def confirm(
        cls, 
        token: str
    ):
        try:
            async with async_session_maker() as session:
                get_confirmation = (
                    select(BookingConfirmations)
                    .filter_by(token=token)
                )
                result = await session.execute(get_confirmation)
                confirmation = result.scalars().first()

                if not confirmation:
                    raise IncorrectTokenFortmatException

                if confirmation.is_expired():
                    raise TokenExpiredException

                if confirmation.is_confirmed:
                    raise BookingAlreadyConfirmedException

                confirmation.is_confirmed = True
                await session.commit()
                return confirmation
            
        except (
            SQLAlchemyError, 
            Exception,
            IncorrectTokenFortmatException,
            TokenExpiredException,
            BookingAlreadyConfirmedException
        ) as e:

            extra = {
                "token": token
            }

            msg="Token isn't found"
            handle_exception(e, IncorrectTokenFortmatException, extra, msg)
            handle_exception(e, TokenExpiredException, extra)
            handle_exception(e, BookingAlreadyConfirmedException, extra)

            handle_db_exception(e, extra)