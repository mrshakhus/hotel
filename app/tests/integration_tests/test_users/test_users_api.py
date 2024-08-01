import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("email, password, status_code", [
    ("shakh@gmail.com", "string", 200),
    ("shakh@gmail.com", "string", 409),
    ("shakh", "string", 422)
])
async def test_register_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post("/v1/auth/register", json={
        "email": email,
        "password": password,
    })

    assert response.status_code == status_code


@pytest.mark.parametrize("email, password, status_code", [
    ("test@test.com", "test", 200),
    ("shakh", "string", 422),
    ("shakh@mail.com", "string", 401),
])
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post("/v1/auth/login", json={
        "email": email,
        "password": password
    })

    assert response.status_code == status_code

async def test_health_check(ac: AsyncClient):
    response = await ac.get("/v1/auth/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}