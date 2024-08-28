from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from app.dao.base import BaseDAO
from app.favorite_hotels.models import FavoriteHotels
from app.hotels.models import Hotels
from app.database import async_session_maker
from app.utils.exception_handlers import handle_db_exception, handle_unexpected_exception

class FavoriteHotelDAO(BaseDAO):
    model = FavoriteHotels

    @classmethod
    async def delete(
        cls,
        favorite_id: int
    ) -> None:
        try:
            async with async_session_maker() as session:
                delete_favorite = (
                    delete(FavoriteHotels)
                    .filter_by(id=favorite_id)
                )
                await session.execute(delete_favorite)
                await session.commit()
        
        except (
            SQLAlchemyError,
            Exception,
        ) as e:

            extra = { 
                "favorite_id": favorite_id
            }

            handle_db_exception(e, extra)
            handle_unexpected_exception(e, extra)

    
    @classmethod
    async def get_favorite_hotels(
        cls,
        user_id: int
    ) -> list[dict]:
        try:
            async with async_session_maker() as session:
                get_hotels = (
                    select(Hotels)
                    .join(
                        FavoriteHotels,
                        FavoriteHotels.hotel_id == Hotels.id
                    )
                    .where(FavoriteHotels.user_id == user_id)
                )

                result = await session.execute(get_hotels)
                result = result.mappings().all()

                hotels = []
                for row in result:
                    hotel = row.Hotels.__dict__.copy()
                    hotel.pop('_sa_instance_state', None)
                    hotels.append(hotel)
                
                return hotels
        
        except (
            SQLAlchemyError,
            Exception,
        ) as e:

            extra = { 
                "user_id": user_id
            }

            handle_db_exception(e, extra)
            handle_unexpected_exception(e, extra)

