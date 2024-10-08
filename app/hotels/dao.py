from datetime import date

from sqlalchemy import and_, case, cast, func, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.exceptions import NoHotelFoundException
from app.favorite_hotels.models import FavoriteHotels
from app.hotels.models import Hotels
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms
from app.utils.exception_handlers import handle_db_exception, handle_exception, validate_dates
from sqlalchemy.exc import SQLAlchemyError

class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def get_all_hotels(
        cls,
        location: str,
        date_from: date,
        date_to: date, 
        min_price: int, 
        max_price: int, 
        hotel_services: list[str]
    ):
        try:
            async with async_session_maker() as session:
                
                needed_rooms = (
                    select(Rooms.id, Rooms.hotel_id)
                    .where(
                        and_(
                            Rooms.price > min_price,
                            Rooms.price < max_price
                        )
                    )
                ).cte("needed_rooms")

                needed_hotels = (
                    select(Hotels.id, Hotels.room_quantity).distinct()
                    .join(
                        needed_rooms,
                        needed_rooms.c.hotel_id == Hotels.id,
                    )
                    .where(
                        and_(
                            Hotels.tsvector.op('@@')(func.to_tsquery('russian', location)),
                            Hotels.services.contains(cast(hotel_services, JSONB))
                        )
                    )
                ).cte("needed_hotels")

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
                    )
                ).cte("all_booked_rooms")

                needed_booked_rooms = (
                    select(Rooms.hotel_id)
                    .select_from(Rooms)
                    .join(
                        all_booked_rooms,
                        all_booked_rooms.c.room_id == Rooms.id
                    )
                ).cte("needed_booked_rooms")

                calc_needed_hotels = (
                    select(
                        needed_hotels.c.id,
                        (needed_hotels.c.room_quantity - func.count(needed_booked_rooms.c.hotel_id))
                        .label('rooms_left')
                    )
                    .select_from(needed_hotels)
                    .join(
                        needed_booked_rooms,
                        needed_booked_rooms.c.hotel_id == needed_hotels.c.id,
                        isouter=True
                    )
                    .group_by(needed_hotels.c.id, needed_hotels.c.room_quantity)
                    .having((needed_hotels.c.room_quantity - func.count(needed_booked_rooms.c.hotel_id)) > 0)
                ).cte("calc_needed_hotels")

                get_needed_hotels = (
                    select(Hotels, calc_needed_hotels.c.rooms_left)
                    .select_from(Hotels)
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
                    hotel.pop('_sa_instance_state', None)
                    hotel['rooms_left'] = row.rooms_left
                    needed_hotels.append(hotel)

                return needed_hotels
            
        except (
            SQLAlchemyError, 
            Exception,
        ) as e:
            
            extra = {
                "location": location, 
                "date_from": date_from, 
                "date_to": date_to, 
                "min_price": min_price, 
                "max_price": max_price, 
                "hotel_services": hotel_services 
            }

            handle_db_exception(e, extra)
        

    @classmethod
    async def get_all_rooms(
        cls,
        hotel_id: int,
        date_from: date,
        date_to: date,
        room_services: list[str]
    ):
        validate_dates(date_from, date_to)
        try:
            async with async_session_maker() as session:
                
                needed_rooms = (
                    select(Rooms)
                    .where(
                        and_(
                            Rooms.hotel_id==hotel_id,
                            Rooms.services.contains(cast(room_services, JSONB))
                        )
                    )
                ).cte("needed_rooms")

                ext_needed_rooms = (
                    select(
                        needed_rooms,
                        ((date_to - date_from).days*needed_rooms.c.price)
                        .label("total_cost")
                    )
                ).cte("ext_needed_rooms")

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

                booked_rooms = (
                    select(all_booked_rooms.c.room_id)
                    .join(
                        Rooms,
                        Rooms.id == all_booked_rooms.c.room_id
                    )
                    .where(Rooms.hotel_id==hotel_id)
                ).cte("booked_rooms")

                rooms_left = (
                    select(
                        ext_needed_rooms.c.id,
                        case(
                            (func.coalesce(func.count(booked_rooms.c.room_id), 0) == 0, ext_needed_rooms.c.quantity),
                            else_=ext_needed_rooms.c.quantity - func.coalesce(func.count(booked_rooms.c.room_id), 0)
                        )
                        .label("rooms_left")
                    )
                    .select_from(ext_needed_rooms)
                    .join(
                        booked_rooms,
                        booked_rooms.c.room_id == ext_needed_rooms.c.id,
                        isouter = True
                    )
                    .group_by(
                        ext_needed_rooms.c.id, ext_needed_rooms.c.quantity, booked_rooms.c.room_id
                    )
                ).cte("rooms_left")

                get_rooms = (
                    select(ext_needed_rooms)
                    .join(
                        rooms_left, 
                        rooms_left.c.id == ext_needed_rooms.c.id
                    )
                    .column(rooms_left.c.rooms_left)
                )

            result = await session.execute(get_rooms)
            result = result.mappings().all()
            return result
        
        except (
            SQLAlchemyError, 
            Exception,
        ) as e:
            
            extra = {
                "hotel_id": hotel_id, 
                "date_from": date_from, 
                "date_to": date_to, 
                "room_services": room_services
            }

            handle_db_exception(e, extra)


    @classmethod
    async def get_hotel(
        cls,
        hotel_id: int
    ):
        try:
            async with async_session_maker() as session:
                get_hotel = (
                    select(Hotels)
                    .where(Hotels.id == hotel_id)
                )

            result = await session.execute(get_hotel)
            hotel = result.mappings().all()

            if not hotel:
                raise NoHotelFoundException

            return hotel[0]["Hotels"]
    
        except (
            SQLAlchemyError,
            NoHotelFoundException, 
            Exception,
        ) as e:
            
            extra = {
                "hotel_id": hotel_id
            }

            handle_exception(e, NoHotelFoundException, extra)

            handle_db_exception(e, extra)