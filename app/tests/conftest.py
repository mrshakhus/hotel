from datetime import datetime

import json
from fastapi_cache import FastAPICache
from httpx import ASGITransport, AsyncClient, patch
from fastapi_cache.backends.inmemory import InMemoryBackend
import pytest
from sqlalchemy import insert
from app.config import settings
from app.database import Base, async_session_maker, engine

from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.users.models import Users
from app.bookings.models import Bookings

from fastapi.testclient import TestClient
from app.main import app as fastapi_app


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", mode="r", encoding="utf-8") as file:
            return json.load(file)
        
    hotels = open_mock_json("hotels")
    rooms = open_mock_json("rooms")
    users = open_mock_json("users")
    bookings = open_mock_json("bookings")

    for booking in bookings:
        booking["date_from"] = datetime.strptime(booking["date_from"], "%Y-%m-%d").date()
        booking["date_to"] = datetime.strptime(booking["date_to"], "%Y-%m-%d").date()

    async with async_session_maker() as session:
        add_hotels = insert(Hotels).values(hotels)
        add_rooms = insert(Rooms).values(rooms)
        add_users = insert(Users).values(users)
        add_bookings = insert(Bookings).values(bookings)

        await session.execute(add_hotels)
        await session.execute(add_rooms)
        await session.execute(add_users)
        await session.execute(add_bookings)

        await session.commit()


# Взято из документации к pytest-asyncio
# @pytest.fixture(scope="session")
# def event_loop():
#     """Create an instance of the default event loop for each test case."""
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close() 



@pytest.fixture(scope="session")
def test_app():
    # Create a test instance of the app
    FastAPICache.init(InMemoryBackend())
    fastapi_app.dependency_overrides = {}
    yield fastapi_app
    FastAPICache.reset()

@pytest.fixture(scope="session")
async def ac(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def authenticated_ac(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/v1/auth/login", json={
            "email": "test@test.com",
            "password": "test",
        })
        assert ac.cookies["booking_access_token"]
        yield ac

    
@pytest.fixture(scope="function")
async def session():
    async with async_session_maker() as session:
        yield session



