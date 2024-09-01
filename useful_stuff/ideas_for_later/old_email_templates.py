# services = ""
    # if booking_info["services"] != []:
    #     services += "<br>Сервисы номера:"
    #     for service in booking_info["services"]:
    #         services += f"<br> - {service}"

    # email.set_content(
    #     f"""
    #         <h1>В отеле "{booking_info["hotel_name"]}" у вас запланировано заселение {string}</h1>
    #         <br>Адрес отеля: {booking_info["location"]}
    #         <br>Название номера: {booking_info["name"]}
    #         <br>Описание номера: {booking_info["description"]}
    #         {services} 
    #         <br>Заселение: {booking_info["date_from"]}
    #         <br>Выселение: {booking_info["date_to"]}
    #     """,
    #     subtype="html"
    # )
# services = ""
    # if booking_info["services"] != []:
    #     services += "<br>Сервисы номера:"
    #     for service in booking_info["services"]:
    #         services += f"<br> - {service}"

    # email.set_content(
    #     f"""
    #         <h1>Вы {string} в отеле "{booking_info["hotel_name"]}"</h1>
    #         <br>Адрес отеля: {booking_info["location"]}
    #         <br>Название номера: {booking_info["name"]}
    #         <br>Описание номера: {booking_info["description"]}
    #         {services} 
    #         <br>Заселение: {booking_info["date_from"]}
    #         <br>Выселение: {booking_info["date_to"]}

    #         <br><a href=http://127.0.0.1:8000/v1/bookings/{booking_info["booking_id"]}/{confirm_type}/{token}>ПОДТВЕРДИТЬ</a>
    #     """,
    #     subtype="html"
    # )