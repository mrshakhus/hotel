from celery import Celery
from celery.schedules import crontab
from app.config import settings



celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=[
        "app.tasks.tasks",
        "app.tasks.scheduled"
    ]
)

celery.conf.beat_schedule = {
    "notification_1": {
        "task": "tomorrow_check_in",
        "schedule": 60
        # "schedule": crontab(minute="0", hour="9")
    },
    # "notification_2": {
    #     "task": "in_3_days_check_in",
    #     "schedule": 10
    #     # "schedule": crontab(minute="30", hour="15")
    # }
}