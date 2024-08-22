from fastapi import HTTPException, status

class BookingException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class TokenAbsentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Отсутствует токен"

class IncorrectTokenFortmatException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена"

class ActionAlreadyConfirmedException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Действие уже было подтверждено"

class TokenExpiredException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен истек"

class UserIsNotPresentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Пользователь не существует"

class UserAlreadyExistsException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже существует"

class IncorrectEmailOrPasswordException(BookingException): #Можно удалить
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверная почта или пароль" 

class AuthenticationRequiredException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Вы должны быть аутентифицированы" 

class RoomCanNotBeBooked(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Комната не может быть забронирована"

class InvalidDatesException(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Указаны некорректные даты"

class MoreThan30DaysException(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Указанный период больше 30 дней"

class CacheDataExpiredException(BookingException):
    status_code=status.HTTP_410_GONE
    detail="Данные истекли или недоступны"

class ServiceUnavailableException(BookingException):
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    detail="Сервис временно недоступен. Пожалуйста, попробуйте позже"

class UnexpectedErrorException(BookingException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже"

class NoRoomFoundException(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Комната отсутствует"

class NoBookingFoundException(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Бронирование отсутствует"

class NoHotelFoundException(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Отель отсутствует"

class NoBookingToDeleteException(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Бронирование для удаления не найдено"

class NoRightsException(BookingException):
    status_code=status.HTTP_403_FORBIDDEN
    detail="У вас нет прав на выполнение этого действия"

class FavoriteHotelAlreadyExistsException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Отель уже добавлен в избранные"

class NoFavoriteHotelException(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Отель отсутствует в избранных"

class RuntimeException(BookingException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Упс... Что-то пошло не так. Попробуйте позже"