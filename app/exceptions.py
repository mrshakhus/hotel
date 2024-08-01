from fastapi import HTTPException, status

class BookingException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class TokenAbsentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Отсутствует токен"

class IncorrectTokenFortmat(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена"

class TokenExpiredException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен истек"

class UserIsNotPresentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED

class UserAlreadyExistsException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже существует"

class IncorrectEmailOrPasswordException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверная почта или пароль" 

class RoomCanNotBeBooked(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Комната не может быть забронирована"

class WrongDatesException(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Указаны некорректные даты"

class MoreThan30DaysException(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Указанный период больше 30 дней"
