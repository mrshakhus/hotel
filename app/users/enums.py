import enum

#TODO в будущем можно вынести этот файл из users
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"