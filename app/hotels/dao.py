from datetime import date

from sqlalchemy import and_, case, func, or_, select
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.hotels.models import Hotels
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def get_all_hotels(
        cls,
        location: str,
        date_from: date,
        date_to: date
    ):
        async with async_session_maker() as session:
            """
            --1.
            WITH needed_hotels AS(
            SELECT id, room_quantity
            FROM hotels
            WHERE location LIKE '%Алтай%'
            ),
            """
            needed_hotels = (
                select(Hotels.id, Hotels.room_quantity)
                .where(Hotels.location.like(f'%{location.strip()}%'))
                .cte("needed_hotels")
                )

            """
            --2.
            all_booked_rooms AS(
            SELECT room_id
            FROM bookings
            WHERE (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                (date_from <= '2023-05-15' AND date_to > '2023-05-15')
            ),
            """
            all_booked_rooms = (
                select(Bookings.room_id).where(
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
                ).cte("all_booked_rooms")
            )

            """
            --3.
            needed_booked_rooms AS(
            SELECT hotel_id
            FROM rooms
            INNER JOIN all_booked_rooms ON all_booked_rooms.room_id = rooms.id
            )
            """
            needed_booked_rooms = (
                select(Rooms.hotel_id)
                .join(
                    all_booked_rooms,
                    all_booked_rooms.c.room_id == Rooms.id
                ).cte("needed_booked_rooms")
            )

            """
            --4.
            calc_needed_hotels AS(
            SELECT needed_hotels.id, needed_hotels.room_quantity - COUNT(needed_booked_rooms.hotel_id)
            AS rooms_left
            FROM needed_hotels 
            LEFT JOIN needed_booked_rooms 
            ON needed_booked_rooms.hotel_id = needed_hotels.id
            GROUP BY needed_hotels.room_quantity, needed_hotels.id
            HAVING needed_hotels.room_quantity - COUNT(needed_booked_rooms.hotel_id) > 0
            )
            """
            calc_needed_hotels = (
                select(
                    needed_hotels.c.id,
                    (needed_hotels.c.room_quantity - func.count(needed_booked_rooms.c.hotel_id))
                    .label('rooms_left')
                )
                .join(
                    needed_booked_rooms,
                    needed_booked_rooms.c.hotel_id == needed_hotels.c.id,
                    isouter=True
                )
                .group_by(needed_hotels.c.id, needed_hotels.c.room_quantity)
                .having((needed_hotels.c.room_quantity - func.count(needed_booked_rooms.c.hotel_id)) > 0)
            ).cte("calc_needed_hotels")

            """
            SELECT * 
            FROM hotels
            INNER JOIN calc_needed_hotels
            ON calc_needed_hotels.id = hotels.id
            """

            get_needed_hotels = (
                select(Hotels, calc_needed_hotels.c.rooms_left)
                .join(
                    calc_needed_hotels,
                    calc_needed_hotels.c.id == Hotels.id
                )
            )

            result = await session.execute(get_needed_hotels)
            result = result.mappings().all()

            needed_hotels = []
            for row in result:
                hotel = row.Hotels.__dict__.copy()
                hotel['rooms_left'] = row.rooms_left
                needed_hotels.append(hotel)

            return needed_hotels
        

    @classmethod
    async def get_all_rooms(
        cls,
        hotel_id: int,
        date_from: date,
        date_to: date
    ):
        async with async_session_maker() as session:
            """
            WITH needed_rooms AS(
                SELECT *
                FROM rooms
                WHERE hotel_id = 1
            ),
            """
            needed_rooms = (
                select(Rooms)
                .where(Rooms.hotel_id==hotel_id)
            ).cte("needed_rooms")

            """
            ext_needed_rooms AS(
                SELECT *, (DATE '2023-06-20' - DATE '2023-05-15')*needed_rooms.price 
                AS total_cost
                FROM needed_rooms
            ),
            """
            ext_needed_rooms = (
                select(
                    needed_rooms,
                    ((date_to - date_from).days*needed_rooms.c.price)
                    .label("total_cost")
                )
            ).cte("ext_needed_rooms")

            """
            all_booked_rooms AS(
                SELECT room_id
                FROM bookings
                WHERE (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                    (date_from <= '2023-05-15' AND date_to > '2023-05-15')
            ),
            """
            all_booked_rooms = (
                select(Bookings.room_id)
                .where(
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
            ).cte("all_booked_rooms")

            """
            booked_rooms AS(
                SELECT room_id
                FROM all_booked_rooms
                INNER JOIN rooms
                ON rooms.id = all_booked_rooms.room_id
                WHERE rooms.hotel_id = 1
            ),
            """
            booked_rooms = (
                select(all_booked_rooms.c.room_id)
                .join(
                    Rooms,
                    Rooms.id == all_booked_rooms.c.room_id
                )
                .where(Rooms.hotel_id==hotel_id)
            ).cte("booked_rooms")

            """
            rooms_left AS(
                SELECT ext_needed_rooms.id,
                    CASE 
                        WHEN COALESCE(booked_rooms.room_id, 0) = 0
                        THEN ext_needed_rooms.quantity
                        ELSE ext_needed_rooms.quantity - COALESCE(COUNT(booked_rooms.room_id), 0)
                    END AS rooms_left
                FROM ext_needed_rooms
                LEFT JOIN booked_rooms
                ON booked_rooms.room_id = ext_needed_rooms.id
                GROUP BY ext_needed_rooms.id, ext_needed_rooms.quantity, booked_rooms.room_id
            )
            """
            rooms_left = (
                select(
                    ext_needed_rooms.c.id,
                    case(
                        (func.coalesce(func.count(booked_rooms.c.room_id), 0) == 0, ext_needed_rooms.c.quantity),
                        else_=ext_needed_rooms.c.quantity - func.coalesce(func.count(booked_rooms.c.room_id), 0)
                    )
                    .label("rooms_left")
                )
                .join(
                    booked_rooms,
                    booked_rooms.c.room_id == ext_needed_rooms.c.id,
                    isouter = True
                )
                .group_by(
                    ext_needed_rooms.c.id, ext_needed_rooms.c.quantity, booked_rooms.c.room_id
                )
            ).cte("rooms_left")

            """
            SELECT * 
            FROM ext_needed_rooms
            LEFT JOIN rooms_left
            ON rooms_left.id = ext_needed_rooms.id
            """
            get_rooms = (
                select(ext_needed_rooms)
                .column(rooms_left.c.rooms_left)
            )

        result = await session.execute(get_rooms)
        result = result.mappings().all()
        return result


    @classmethod
    async def get_hotel(
        cls,
        hotel_id: int
    ):
        async with async_session_maker() as session:
            get_hotel = (
                select(Hotels)
                .where(Hotels.id == hotel_id)
            )

        result = await session.execute(get_hotel)
        result = result.mappings().all()
        return result