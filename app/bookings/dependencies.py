from fastapi import Depends
from app.bookings.dao import BookingConfirmationDAO
from app.users.dependencies import get_current_user
from app.users.models import Users


async def get_confirmation_token(user: Users = Depends(get_current_user)):
    confirmation_token = await BookingConfirmationDAO.create(user.id)
    return confirmation_token