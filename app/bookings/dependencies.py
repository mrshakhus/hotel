import smtplib
from fastapi import Depends
from app.bookings.dao import BookingConfirmationDAO
from app.config import settings
from app.tasks.email_templates import create_booking_confirmation_link_template
from app.users.dependencies import get_current_user
from app.users.models import Users


async def get_confirmation_token(user: Users = Depends(get_current_user)):
    confirmation_token = await BookingConfirmationDAO.create(user.id)
    return confirmation_token

#for test
async def send_confirmation_email_with_link(email: str, token: str):
    msg_content = await create_booking_confirmation_link_template(email, token)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
#for test