from datetime import date

from sqlalchemy import DATE, func, select

from app.users.models import Users
from app.hotels.rooms.models import Rooms
from app.hotels.models import Hotels
from app.bookings.models import Bookings
from app.database import async_session_maker


class BookingTaskDAO():
    @classmethod
    async def get_users_for_notification(
        cls,
        date_from: date,
        days_before_check_in: int
    ):
        # Из бд надо достать бронирования
        # посмотреть, у кого заезд завтра
        # найдя такого пользователя, ему на почту отправить письмо
        async with async_session_maker() as session:
            """
            WITH needed_bookings AS(
                SELECT user_id, date_from
                FROM bookings
                WHERE(date_from - DATE '2030-06-05' = 1)
            ),
            """
            needed_bookings = (
            select(Bookings.user_id, Bookings.date_from, Bookings.date_to)
            .where(
                (Bookings.date_from - date_from) == days_before_check_in
            )
        ).cte("needed_bookings")

            """
            users_to_inform AS(
                SELECT user_id, users.email,
                COUNT(needed_bookings.user_id)
                FROM needed_bookings
                LEFT JOIN users 
                ON users.id = needed_bookings.user_id
                GROUP BY needed_bookings.user_id, users.email
            )

            SELECT * FROM users_to_inform
            """
            users_to_inform = (
                select(
                    needed_bookings.c.user_id, 
                    Users.email,
                    func.count(needed_bookings.c.user_id)
                    .label("room_quantity"),
                    needed_bookings.c.date_from,
                    needed_bookings.c.date_to
                )
                .join(
                    Users,
                    Users.id == needed_bookings.c.user_id,
                    isouter=True
                )
                .group_by(
                    needed_bookings.c.user_id, 
                    Users.email, 
                    needed_bookings.c.date_from,
                    needed_bookings.c.date_to
                )
            ).cte("users_to_inform")

            get_needed_users = select(users_to_inform)

            result = await session.execute(get_needed_users)
            users = result.mappings().all()
        
        return users