import enum

class BookingAction(int, enum.Enum):
    CONFIRM = 1
    CANCEL = 2


class BookingStatus(int, enum.Enum):
    ACTIVE = 1
    COMPLETED = 2
    CANCELLED = 3
    EXPIRED = 4
    PENDING = 5
    
