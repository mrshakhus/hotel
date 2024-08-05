from datetime import date, datetime, timedelta, timezone
import secrets

from sqlalchemy import and_, delete, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError
from app.bookings.models import Bookings, BookingConfirmation
from app.bookings.schemas import SBooking
from app.dao.base import BaseDAO
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
        """
        WITH booked_rooms AS(
        SELECT * FROM bookings
        WHERE room_id = 1 AND
        (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
        (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        )
        """
        try:
            async with async_session_maker() as session:
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
                # print(rooms_left)

                if int(rooms_left) > 0:
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
                    # result = booking.scalars().one()
                    result = booking.mappings().one()["Bookings"]
                    # return SBooking.from_orm(result)
                    return SBooking.model_validate(result) 
                else:
                    return None
        #В других классах DAO тоже писать try-except
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot add booking"
            extra = {
                "user_id": user_id, 
                "room_id": room_id, 
                "date_from": date_from, 
                "date_to": date_to
            }
            logger.error(msg, extra=extra, exc_info=True)


    @classmethod
    async def delete(
        cls,
        user_id: int,
        booking_id: int,
    ):
        async with async_session_maker() as session:
            delete_booking = delete(Bookings).filter_by(id=booking_id, user_id=user_id)
            await session.execute(delete_booking)
            await session.commit()


class BookingConfirmationDAO(BaseDAO):
    model = BookingConfirmation

    @classmethod
    async def create(cls, user_id: int):
        token = secrets.token_urlsafe()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        async with async_session_maker() as session:
            confirmation = {
                "user_id": user_id,
                "token": token,
                "expires_at": expires_at.replace(tzinfo=None)
            }

            add_confimation = (
                insert(BookingConfirmation)
                .values(confirmation)
            )
            await session.execute(add_confimation)
            await session.commit()
            return token


    @classmethod
    async def confirm(cls, token: str):
        async with async_session_maker() as session:
            get_confirmation = (
                select(BookingConfirmation)
                .filter_by(token=token)
            )
            result = await session.execute(get_confirmation)
            confirmation = result.scalars().first()

            if confirmation and not confirmation.is_expired() and not confirmation.is_confirmed:
                confirmation.is_confirmed = True
                await session.commit()
                return confirmation
            return None