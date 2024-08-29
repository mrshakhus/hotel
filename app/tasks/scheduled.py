import asyncio
from datetime import datetime, timezone
import smtplib
from app.exceptions import BookingAPIException
from app.tasks.celery import celery
from app.tasks.dao import BookingTaskDAO
from app.tasks.email_templates import create_booking_notification_template
from app.config import settings
from app.utils.exception_handlers import handle_exception, handle_unexpected_exception


async def send_notification_email(
    days_before_check_in: int
) -> None:
    try:
        todays_date = datetime.now(timezone.utc).date()
        users = await BookingTaskDAO.get_users_for_notification(todays_date, days_before_check_in)

        if not users:
            print("NO USERS FOUND FOR NOTIFICATION")
            return
        
        for user in users:
            msg_content = create_booking_notification_template(user, days_before_check_in)

            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg_content)
    
    except (
        BookingAPIException,
        Exception
    ) as e:
        extra = {
            "days_before_check_in": days_before_check_in
        }
        handle_exception(e, BookingAPIException, extra)
        handle_unexpected_exception(e, extra)


@celery.task(name="tomorrow_check_in")
def check_in_tomorrow() -> None:
    try:
        print("AWAITING T")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            send_notification_email(1)
        )
        print("DONE T")

    except (
        BookingAPIException,
        Exception
    ) as e:
        handle_exception(e, BookingAPIException)
        handle_unexpected_exception(e)


@celery.task(name="in_3_days_check_in")
def check_in_in_3_days() -> None:
    #15:30
    try:
        print("AWAITING 3")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            send_notification_email(3)
        )
        print("DONE 3")
        
    except (
        BookingAPIException,
        Exception
    ) as e:
        handle_exception(e, BookingAPIException)
        handle_unexpected_exception(e)


    