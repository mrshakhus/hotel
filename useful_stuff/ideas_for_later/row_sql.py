#BookingDAO
    #add

"""
WITH booked_rooms AS(
SELECT * FROM bookings
WHERE room_id = 1 AND
(date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
(date_from <= '2023-05-15' AND date_to > '2023-05-15')
)
"""
"""
SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms 
LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
WHERE rooms.id = 1
GROUP BY rooms.quantity, booked_rooms.room_id
"""

    #get_all_hotels

"""
WITH needed_rooms AS(
    SELECT id, hotel_id
    FROM rooms
    WHERE price > 100 
    AND price < 100000
),
""" 
""" 
needed_hotels AS(
    SELECT DISTINCT hotels.id, hotels.room_quantity
    FROM hotels
    LEFT JOIN needed_rooms
    ON needed_rooms.hotel_id = hotels.id
    WHERE hotels.location LIKE '%Алтай%'
    AND (
        SELECT COUNT(DISTINCT service)
        FROM json_array_elements_text(hotels.services::json) AS service
        WHERE service IN ('Wi-Fi', 'Парковка')
    ) = 2
),
"""
"""
all_booked_rooms AS(
SELECT room_id
FROM bookings
WHERE (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
    (date_from <= '2023-05-15' AND date_to > '2023-05-15')
),
"""

"""
needed_booked_rooms AS(
SELECT hotel_id
FROM rooms
INNER JOIN all_booked_rooms ON all_booked_rooms.room_id = rooms.id
)
"""
"""
calc_needed_hotels AS(
SELECT needed_hotels.id, needed_hotels.room_quantity - COUNT(needed_booked_rooms.hotel_id)
AS rooms_left
FROM needed_hotels 
LEFT JOIN needed_booked_rooms 
ON needed_booked_rooms.hotel_id = needed_hotels.id
GROUP BY needed_hotels.room_quantity, needed_hotels.id
HAVING needed_hotels.room_quantity - COUNT(needed_booked_rooms.hotel_id) > 0
)
"""
"""
SELECT * 
FROM hotels
INNER JOIN calc_needed_hotels
ON calc_needed_hotels.id = hotels.id
"""

 #get_all_rooms

"""
WITH needed_rooms AS(
    SELECT *
    FROM rooms
    WHERE hotel_id = 1
),
"""
"""
ext_needed_rooms AS(
    SELECT *, (DATE '2023-06-20' - DATE '2023-05-15')*needed_rooms.price 
    AS total_cost
    FROM needed_rooms
),
"""
"""
all_booked_rooms AS(
    SELECT room_id
    FROM bookings
    WHERE (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
        (date_from <= '2023-05-15' AND date_to > '2023-05-15')
),
"""
"""
booked_rooms AS(
    SELECT room_id
    FROM all_booked_rooms
    INNER JOIN rooms
    ON rooms.id = all_booked_rooms.room_id
    WHERE rooms.hotel_id = 1
),
"""
"""
rooms_left AS(
    SELECT ext_needed_rooms.id,
        CASE 
            WHEN COALESCE(booked_rooms.room_id, 0) = 0
            THEN ext_needed_rooms.quantity
            ELSE ext_needed_rooms.quantity - COALESCE(COUNT(booked_rooms.room_id), 0)
        END AS rooms_left
    FROM ext_needed_rooms
    LEFT JOIN booked_rooms
    ON booked_rooms.room_id = ext_needed_rooms.id
    GROUP BY ext_needed_rooms.id, ext_needed_rooms.quantity, booked_rooms.room_id
)
"""
"""
SELECT * 
FROM ext_needed_rooms
LEFT JOIN rooms_left
ON rooms_left.id = ext_needed_rooms.id
"""

    #get_full_info_by_room_id
            
"""
WITH booked_room AS(
    SELECT hotel_id, name, description, services 
    FROM rooms
    WHERE rooms.id = 1
),
"""
"""
booked_hotel AS(
    SELECT hotels.name
    AS "hotel_name"
    , hotels.location 
    FROM hotels
    JOIN booked_room
    ON hotels.id = booked_room.hotel_id
)
"""
"""
SELECT * FROM booked_room, booked_hotel
"""

#BookingTaskDAO
#get_users_for_notification
# async with async_session_maker() as session:
#     """
#     WITH needed_bookings AS(
#         SELECT user_id, date_from
#         FROM bookings
#         WHERE(date_from - DATE '2030-06-05' = 1)
#     ),
#     """
#     needed_bookings = (
#     select(
#         Bookings.user_id, 
#         Bookings.date_from, 
#         Bookings.date_to
#     )
#     .where(
#         (Bookings.date_from - todays_date) == days_before_check_in
#     )
# ).cte("needed_bookings")

#     """
#     users_to_inform AS(
#         SELECT user_id, users.email,
#         COUNT(needed_bookings.user_id)
#         FROM needed_bookings
#         LEFT JOIN users 
#         ON users.id = needed_bookings.user_id
#         GROUP BY needed_bookings.user_id, users.email
#     )

#     SELECT * FROM users_to_inform
#     """
#     users_to_inform = (
#         select(
#             needed_bookings.c.user_id, 
#             Users.email,
#             func.count(needed_bookings.c.user_id)
#             .label("room_quantity"),
#             needed_bookings.c.date_from,
#             needed_bookings.c.date_to
#         )
#         .join(
#             Users,
#             Users.id == needed_bookings.c.user_id,
#             isouter=True
#         )
#         .group_by(
#             needed_bookings.c.user_id, 
#             Users.email, 
#             needed_bookings.c.date_from,
#             needed_bookings.c.date_to
#         )
#     ).cte("users_to_inform")

#     get_needed_users = select(users_to_inform)

#     result = await session.execute(get_needed_users)
#     users = result.mappings().all()
#     print(type(users))