import smtplib
from typing import Any
from fastapi import Depends
from app.bookings.dao import BookingConfirmationDAO
from app.config import settings
from app.tasks.email_templates import create_booking_confirmation_link_template
from app.users.dependencies import get_current_user
from app.users.models import Users
from fastapi_cache import FastAPICache
import json


async def set_cache(key: str, value: Any, expire: int):
    await FastAPICache.get_backend().set(key, json.dumps(value), expire=expire)

async def get_cache(key: str):
    value = await FastAPICache.get_backend().get(key)
    if value:
        return json.loads(value)
    return None


#for test
async def send_confirmation_email_with_link(booking_info: dict, token: str):
    msg_content = await create_booking_confirmation_link_template(booking_info, token)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
#for test