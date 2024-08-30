from email.message import EmailMessage
from app.bookings.enums import BookingAction
from app.config import settings


def create_booking_notification_template(
        booking_info: dict,
        days_before_check_in: int
):
    email = EmailMessage()
    days_left = ""

    if days_before_check_in == 1:
        email["Subject"] = "У вас завтра заселение"
        days_left = "завтра"
    elif days_before_check_in == 3:
        email["Subject"] = "Осталось 3 дня до заселения"
        days_left = "через 3 дня"

    email["From"] = settings.SMTP_USER
    email["To"] = booking_info["user_email"]

    services = ""
    if booking_info["services"]:
        services += "<h3 style='color: #333;'>Сервисы номера:</h3>"
        services += "<ul style='padding-left: 20px;'>"
        for service in booking_info["services"]:
            services += f"<li style='margin-bottom: 5px;'>{service}</li>"
        services += "</ul>"

    email.set_content(
        f"""
        <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <h1 style="color: #4CAF50; text-align: center;">Отель "{booking_info["hotel_name"]}" ждет вас {days_left}!</h1>
            <p style="font-size: 16px; margin-bottom: 20px;">
                У вас запланировано заселение в отеле <strong>"{booking_info["hotel_name"]}"</strong> {days_left}.
            </p>
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9;">
                <h2 style="color: #4CAF50;">Информация о заселении:</h2>
                <p><strong>Адрес отеля:</strong> {booking_info["location"]}</p>
                <p><strong>Название номера:</strong> {booking_info["name"]}</p>
                <p><strong>Описание номера:</strong> {booking_info["description"]}</p>
                {services}
                <p><strong>Заселение:</strong> {booking_info["date_from"]}</p>
                <p><strong>Выселение:</strong> {booking_info["date_to"]}</p>
            </div>
            <p style="text-align: center; margin-top: 30px; font-size: 14px; color: #888;">
                Ждем вас в нашем отеле! Приятного отдыха!
            </p>
        </div>
        """,
        subtype="html"
    )

    return email


def create_booking_confirmation_link_template(
    booking_info: dict,
    token: str
):
    print(booking_info)

    email = EmailMessage()
    email["From"] = settings.SMTP_USER
    email["To"] = booking_info["user_email"]
    
    if booking_info["action"] == BookingAction.CONFIRM:
        email["Subject"] = "Подтверждение бронирования"
        confirm_type = f"confirmations"
        action = "Подтвердите бронирование номера"
    else:
        email["Subject"] = "Подтверждение отмены бронирования"
        confirm_type = f"cancellation_confirmations"
        action = "Подтвердите отмену бронирования номера"

    services = ""
    if booking_info["services"]:
        services += "<h3 style='color: #333;'>Сервисы номера:</h3>"
        services += "<ul style='padding-left: 20px;'>"
        for service in booking_info["services"]:
            services += f"<li style='margin-bottom: 5px;'>{service}</li>"
        services += "</ul>"

    email.set_content(
        f"""
        <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <h1 style="color: #4CAF50; text-align: center;">{action} в отеле "{booking_info["hotel_name"]}"</h1>
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9;">
                <p><strong>Адрес отеля:</strong> {booking_info["location"]}</p>
                <p><strong>Название номера:</strong> {booking_info["name"]}</p>
                <p><strong>Описание номера:</strong> {booking_info["description"]}</p>
                {services}
                <p><strong>Заселение:</strong> {booking_info["date_from"]}</p>
                <p><strong>Выселение:</strong> {booking_info["date_to"]}</p>
                <p style="text-align: center; margin-top: 20px;">
                    <a href="http://localhost:7777/v1/bookings/{confirm_type}/{token}" 
                       style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #4CAF50; text-decoration: none; border-radius: 5px;">
                       ПОДТВЕРДИТЬ
                    </a>
                </p>
            </div>
            <p style="text-align: center; margin-top: 30px; font-size: 14px; color: #888;">
                Спасибо за использование нашего сервиса!
            </p>
        </div>
        """,
        subtype="html"
    )

    return email