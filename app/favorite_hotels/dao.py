from sqlalchemy import delete, select
from app.dao.base import BaseDAO
from app.favorite_hotels.models import FavoriteHotels
from app.hotels.models import Hotels
from app.database import async_session_maker

class FavoriteHotelDAO(BaseDAO):
    model = FavoriteHotels

    @classmethod
    async def delete(
        cls,
        favorite_id: int
    ):
        async with async_session_maker() as session:
            delete_favorite = (
                delete(FavoriteHotels)
                .filter_by(id=favorite_id)
            )
            await session.execute(delete_favorite)
            await session.commit()

    
    @classmethod
    async def get_favorite_hotels(
        cls,
        user_id: int
    ):
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

