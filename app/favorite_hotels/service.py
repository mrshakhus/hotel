from app.exceptions import BookingAPIException, FavoriteHotelAlreadyExistsException, NoFavoriteHotelException, NoHotelFoundException
from app.favorite_hotels.dao import FavoriteHotelDAO
from app.hotels.dao import HotelDAO
from app.utils.exception_handlers import handle_exception, handle_unexpected_exception
 

class FavoriteHotelsService:
    @staticmethod
    async def add_hotel_to_favorites(
        user_id: int, 
        hotel_id: int
    ) -> None:
        try:
            hotel = await HotelDAO.find_one_or_none(id=hotel_id)
            if not hotel:
                raise NoHotelFoundException
            
            favorite_hotel = await FavoriteHotelDAO.find_one_or_none(user_id=user_id, hotel_id=hotel_id)
            if favorite_hotel:
                raise FavoriteHotelAlreadyExistsException
            
            await FavoriteHotelDAO.add_booking(user_id=user_id, hotel_id=hotel_id)
        
        except (
            NoHotelFoundException,
            FavoriteHotelAlreadyExistsException,
            BookingAPIException,
            Exception,
        ) as e:

            extra = { 
                "user_id": user_id, 
                "hotel_id": hotel_id
            }

            handle_exception(e, NoHotelFoundException, extra)
            handle_exception(e, FavoriteHotelAlreadyExistsException, extra)
            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)
    

    @staticmethod
    async def delete_hotel_from_favorites(
        favorite_id: int
    ) -> None:
        try:
            favorite_hotel = await FavoriteHotelDAO.find_one_or_none(id=favorite_id)
            if not favorite_hotel:
                raise NoFavoriteHotelException
            
            await FavoriteHotelDAO.delete(favorite_id)
        
        except (
            NoFavoriteHotelException,
            BookingAPIException,
            Exception,
        ) as e:
            
            extra = { 
                "favorite_id": favorite_id
            }

            handle_exception(e, NoFavoriteHotelException, extra)
            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)


    @staticmethod
    async def get_favorite_hotels(
        user_id: int
    ) -> list[dict]:
        try:
            hotels = await FavoriteHotelDAO.get_favorite_hotels(user_id)
            return hotels

        except (
            BookingAPIException,
            Exception 
        ) as e:
            
            extra = { 
                "user_id": user_id
            }

            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)