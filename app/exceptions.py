from fastapi import HTTPException, status

class BookingAPIException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class TokenAbsentException(BookingAPIException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Отсутствует токен"

class IncorrectTokenFortmatException(BookingAPIException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена"

class ActionAlreadyConfirmedException(BookingAPIException):
    status_code=status.HTTP_409_CONFLICT
    detail="Действие уже было подтверждено"

class TokenExpiredException(BookingAPIException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен истек"

class UserIsNotPresentException(BookingAPIException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Пользователь не существует"

class UserAlreadyExistsException(BookingAPIException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже существует"

class IncorrectPasswordException(BookingAPIException): 
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Введеный пароль неверный" 

class AuthenticationRequiredException(BookingAPIException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Вы должны быть аутентифицированы" 

class RoomCanNotBeBooked(BookingAPIException):
    status_code=status.HTTP_409_CONFLICT
    detail="Комната не может быть забронирована"

class InvalidDatesException(BookingAPIException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Указаны некорректные даты"

class MoreThan30DaysException(BookingAPIException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Указанный период больше 30 дней"

class CacheDataExpiredException(BookingAPIException):
    status_code=status.HTTP_410_GONE
    detail="Данные истекли или недоступны"

class ServiceUnavailableException(BookingAPIException):
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    detail="Сервис временно недоступен. Пожалуйста, попробуйте позже"

class NoRoomFoundException(BookingAPIException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Комната отсутствует"

class NoBookingFoundException(BookingAPIException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Бронирование отсутствует"

class NoHotelFoundException(BookingAPIException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Отель отсутствует"

class NoBookingToDeleteException(BookingAPIException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Бронирование для удаления не найдено"

class NoRightsException(BookingAPIException):
    status_code=status.HTTP_403_FORBIDDEN
    detail="У вас нет прав на выполнение этого действия"

class FavoriteHotelAlreadyExistsException(BookingAPIException):
    status_code=status.HTTP_409_CONFLICT
    detail="Отель уже добавлен в избранные"

class NoFavoriteHotelException(BookingAPIException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Отель отсутствует в избранных"

class UnexpectedError(BookingAPIException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Произошла неожиданная ошибка. Попробуйте позже"

class PasswordsDoNotMatchException(BookingAPIException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Пароли не совпадают"