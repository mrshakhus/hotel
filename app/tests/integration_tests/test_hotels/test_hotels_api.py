from httpx import AsyncClient
import pytest

@pytest.mark.parametrize("location, date_from, date_to, status_code", [
    ("Алтай", "2023-10-31", "2023-10-01", 400),
    ("Алтай", "2023-10-31", "2023-12-01", 400)
])
async def test_get_hotels(location, date_from, date_to, status_code, ac: AsyncClient):
    response = await ac.get(f"/v1/hotels/{location}", params={
        "location": location,
        "date_from": date_from,
        "date_to": date_to
    })

    assert response.status_code == status_code
