from datetime import date
from email.message import EmailMessage
from pydantic import EmailStr
from app.bookings.enums import ConfirmationAction
from app.config import settings


async def create_booking_notification_template(
        email_to: EmailStr,
        date_from: date,
        date_to: date,
        days_before_check_in: int
):
    email = EmailMessage()

    if days_before_check_in == 1:
        email["Subject"] = "У вас завтра заселение"
    elif days_before_check_in == 3:
        email["Subject"] = "Осталось 3 дня до заселения"

    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
            <h1>Напоминание о бронировании</h1>
            Вы бронировали отель с {date_from} по {date_to}
        """,
        subtype="html"
    )

    return email


async def create_booking_confirmation_link_template(booking_info: dict, token: str):
    print(booking_info)

    email = EmailMessage()
    email["From"] = settings.SMTP_USER
    email["To"] = booking_info["user_email"]
    
    if booking_info["action"] == ConfirmationAction.CREATE:
        email["Subject"] = "Подтверждение бронирования"
        confirm_type = f"confirmations"
        string = "бронировали номер"
    else:
        email["Subject"] = "Подтверждение отмены бронирования"
        confirm_type = f"cancellation_confirmation"
        string = "отменяете бронирование номера"

    services = ""
    if booking_info["services"] != []:
        services += "<br>Сервисы номера:"
        for service in booking_info["services"]:
            services += f"<br> - {service}"

    email.set_content(
        f"""
            <h1>Вы {string} в отеле "{booking_info["hotel_name"]}"</h1>
            <br>Адрес отеля: {booking_info["location"]}
            <br>Название номера: {booking_info["name"]}
            <br>Описание номера: {booking_info["description"]}
            {services} 
            <br>Заселение: {booking_info["date_from"]}
            <br>Выселение: {booking_info["date_to"]}

            <br><a href=http://127.0.0.1:8000/v1/bookings/{booking_info["booking_id"]}/{confirm_type}/{token}>ПОДТВЕРДИТЬ</a>
        """,
        subtype="html"
    )

    return email