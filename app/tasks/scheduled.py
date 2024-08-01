import asyncio
from datetime import datetime, timezone
import smtplib
from app.tasks.celery import celery
from app.tasks.dao import BookingTaskDAO
from app.tasks.email_templates import create_booking_notification_template
from app.config import settings


async def send_notification_email(days_before_check_in):

    todays_date = datetime.now(timezone.utc).date()
    users = await BookingTaskDAO.get_users_for_notification(todays_date, days_before_check_in)
    print(todays_date)
    print(users)

    if len(users) != 0:
        for user in users:
            msg_content = await create_booking_notification_template(
                user["email"], 
                user["date_from"],
                user["date_to"],
                days_before_check_in
            )
            print(msg_content)

            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                print("SENDING")
                server.send_message(msg_content)
                print("SENT")
    else:
        print("NO USERS FOUND")


@celery.task(name="tomorrow_check_in")
async def tomorrow_check_in():
    """
    Таска будет напоминать о бронировании тем пользователям, у кого на завтра запланирован заезд в отель. Таска/функция должна выполняться каждый день в 9 утра (задайте через crontab)
    """
    print("AWAITING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    await send_notification_email(1)
    print("AWAITED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

# @celery.task(name="in_3_days_check_in")
# async def in_3_days_check_in():
#     """
#     Вторая таска будет напоминать о бронировании тем пользователям, у кого через 3 дня запланирован заезд в отель. Таска/функция должна выполняться каждый день в 15:30 утра (задайте через crontab)
#     """
#     print("AWAITING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#     await send_notification_email(3)
#     print("AWAITED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    