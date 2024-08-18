import enum

class ConfirmationAction(int, enum.Enum):
    CREATE = 1
    CANCEL = 2


class BookingStatus(int, enum.Enum):
    ACTIVE = 1
    COMPLETED = 2
    CANCELLED = 3
    EXPIRED = 4
    
