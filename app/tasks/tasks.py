import asyncio
from pathlib import Path
import smtplib
from app.config import settings

from app.exceptions import BookingAPIException
from app.tasks.celery import celery
from PIL import Image

from app.tasks.dao import BookingTaskDAO
from app.tasks.email_templates import create_booking_confirmation_link_template
from app.utils.exception_handlers import handle_exception, handle_unexpected_exception


@celery.task
def process_pic(
     path: str
):
    im_path = Path(path)
    im = Image.open(im_path)

    im_resized_1000_500 = im.resize((1000, 500))
    im_resized_200_100 = im.resize((200, 100))
    im_resized_1000_500.save(f"app/static/images/resized_1000_500_{im_path.name}")
    im_resized_200_100.save(f"app/static/images/resized_200_100_{im_path.name}")


@celery.task
def send_confirmation_email_with_link(
    booking_info: dict, 
    token: str
) -> None:
    try:
        msg_content = create_booking_confirmation_link_template(booking_info, token)

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_content)
    
    except (
        Exception
    ) as e:
        extra = {
            "booking_info": booking_info,
            "token": token
        }
        handle_unexpected_exception(e, extra)


async def set_status_expired(
    booking_id: int  
):
    try:
        await BookingTaskDAO.set_booking_status_expired(booking_id)

    except (
        BookingAPIException,
        Exception
    ) as e:
        extra = {
            "booking_id": booking_id
        }
        handle_exception(e, BookingAPIException, extra)
        handle_unexpected_exception(e, extra)


@celery.task
def set_booking_status_expired(
    booking_id: int
) -> None:
    try:
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(
        #     set_status_expired(booking_id)
        # )

        loop = asyncio.get_event_loop()
        if loop.is_running():
            print("RUNNING")
            # If there's an existing loop, use asyncio.ensure_future to run the coroutine
            asyncio.ensure_future(set_status_expired(booking_id))
        else:
            print("CREATED NEW LOOP")
            # Run the coroutine in a new event loop if none is running
            loop.run_until_complete(set_status_expired(booking_id))
    
    except (
        BookingAPIException,
        Exception
    ) as e:
        extra = {
            "booking_id": booking_id
        }
        handle_exception(e, BookingAPIException, extra)
        handle_unexpected_exception(e, extra)