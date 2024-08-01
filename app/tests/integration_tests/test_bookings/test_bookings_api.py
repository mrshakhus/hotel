import json
from httpx import AsyncClient
import pytest


@pytest.mark.parametrize("room_id, date_from, date_to, rooms_booked, status_code", [
    (4, "2030-05-01", "2030-05-09", 3, 200),
    (4, "2030-05-01", "2030-05-09", 4, 200),
    (4, "2030-05-01", "2030-05-09", 5, 200),
    (4, "2030-05-01", "2030-05-09", 6, 200),
    (4, "2030-05-01", "2030-05-09", 7, 200),
    (4, "2030-05-01", "2030-05-09", 8, 200),
    (4, "2030-05-01", "2030-05-09", 9, 200),
    (4, "2030-05-01", "2030-05-09", 10, 200),
    (4, "2030-05-01", "2030-05-09", 10, 409),
    (4, "2030-05-01", "2030-05-09", 10, 409),
])
async def test_add_and_get_booking(
    room_id, date_from, date_to, rooms_booked, status_code, authenticated_ac: AsyncClient
):
    response = await authenticated_ac.post("/v1/bookings", params={
        "room_id": room_id,
        "date_from": date_from,
        "date_to": date_to
    })

    assert response.status_code == status_code

    bookings = await authenticated_ac.get("/v1/bookings")

    assert len(bookings.json()) == rooms_booked


"""
Получение и удаление бронирований (API-интеграционный-тест)

Давайте попробуем протестировать работу наших эндпоинтов в связке. Сперва получим все бронирования текущего аутентифицированного пользователя через GET /bookings, а затем удалим их всех в цикле через DELETE /bookings/{id}, после чего проверим через GET /bookings, что у пользователя не осталось бронирований.
*По желанию данный тест можно параметризировать для нескольких пользователей.
"""

@pytest.mark.parametrize("authenticated_ac", [
    {"email": "test@test.com", "password": "test"},
    {"email": "artem@example.com", "password": "artem"}
], indirect=True)
async def test_get_and_delete_bookings(authenticated_ac: AsyncClient):
    bookings = await authenticated_ac.get("/v1/bookings")

    for booking in bookings.json():
        await authenticated_ac.delete(f"/v1/bookings/{booking["id"]}")

    bookings = await authenticated_ac.get("/v1/bookings")

    assert len(bookings.json()) == 0


"""
Работа с бронированиями через БД (интеграционный тест)

Необходимо протестировать CRUD операции с бронированиями:

Добавление брони (данная операция возвращает id добавленной записи)
Чтение брони (используя полученный id)
Удаление брони
Чтение брони (необходимо убедиться, что бронь удалилась)
"""
@pytest.mark.parametrize("authenticated_ac, room_id, date_from, date_to, status_code", [
    ({"email": "test@test.com", "password": "test"},
     2, "2023-10-31", "2023-10-01", 200 
     ),
    ({"email": "artem@example.com", "password": "artem"},
     2, "2023-10-31", "2023-10-01", 200, 
     )
], indirect=["authenticated_ac"])
async def test_CRUD_operations_on_bookings(
    authenticated_ac: AsyncClient, room_id, date_from, date_to, status_code
):
    new_booking = await authenticated_ac.post("/v1/bookings", params={
        "room_id": room_id,
        "date_from": date_from,
        "date_to": date_to
    })

    assert new_booking.status_code == status_code


    bookings = await authenticated_ac.get("/v1/bookings")
    added_booking = None
    for booking in bookings.json():
        if booking["id"] == new_booking.json()["id"]:
            added_booking = booking

    assert added_booking is not None


    await authenticated_ac.delete(f"/v1/bookings/{added_booking["id"]}")

    bookings = await authenticated_ac.get("/v1/bookings")
    added_booking = None
    for booking in bookings.json():
        if booking["id"] == new_booking.json()["id"]:
            added_booking = booking

    assert added_booking is None