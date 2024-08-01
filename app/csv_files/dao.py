import json
from pandas import DataFrame
from sqlalchemy import insert, select
from app.database import engine
from app.hotels.models import Hotels
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class SCV_files():
    @classmethod
    async def add_hotels(
        cls,
        df: DataFrame
    ):
        async with async_session_maker() as session:
            for _, row in df.iterrows():
                services = row['services'].replace("'",'"')
                hotel = {
                    "name": row['name'],
                    "location": row['location'],
                    "services": json.loads(services),
                    "room_quantity": row['room_quantity'],
                    "image_id": row['image_id']
                }

                add_hotel = (
                    insert(Hotels)
                    .values(hotel)
                )
                await session.execute(add_hotel)

            await session.commit()


    @classmethod
    async def add_rooms(
        cls,
        df: DataFrame
    ):
        async with async_session_maker() as session:
            for _, row in df.iterrows():
                services = row['services'].replace("'",'"')
                room = {
                    "hotel_id": row["hotel_id"],
                    "name": row["name"],
                    "description": row["description"],
                    "price": row["price"],
                    "services": json.loads(services),
                    "quantity": row["quantity"],
                    "image_id": row["image_id"],
                }

                add_room = (
                    insert(Rooms)
                    .values(room)
                )
                await session.execute(add_room)

            await session.commit()