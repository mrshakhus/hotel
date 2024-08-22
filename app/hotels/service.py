from datetime import date

from app.hotels.dao import HotelDAO
from app.hotels.dependencies import format_query


class HotelsService:
    @staticmethod
    async def get_hotels(
        location: str,
        date_from: date,
        date_to: date,
        min_price: int,
        max_price: int,
        hotel_services: list[str]
    ):
        location = format_query(location)

        hotels = await HotelDAO.get_all_hotels(
            location, 
            date_from, 
            date_to,
            min_price,
            max_price,
            hotel_services
        )

        return hotels