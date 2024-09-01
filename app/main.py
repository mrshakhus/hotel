from contextlib import asynccontextmanager
import sentry_sdk
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from app import limiter
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.admin.auth import authentication_backend
from app.config import settings
from app.database import engine
from app.bookings.router import router as bookings_router
from app.users.router import router as users_router
from app.hotels.router import router as hotels_router
from app.csv_files.router import router as csv_files_router
from app.favorite_hotels.router import router as favorite_hotels_router
from app.logger import logger
from fastapi_versioning import VersionedFastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


sentry_sdk.init(
    dsn="https://c454e49e1eef029a7828e0ee29639197@o4507515494596608.ingest.de.sentry.io/4507515501346896",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="cache")
        yield
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        await redis.close()


app = FastAPI(
    title="Бронирование Отелей",
    lifespan=lifespan
)


app.include_router(users_router)
app.include_router(hotels_router)
app.include_router(bookings_router)
app.include_router(csv_files_router)
app.include_router(favorite_hotels_router)

origins = [
    # 3000 - порт, на котором работает фронтенд на React.js 
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", 
                   "Access-Control-Allow-Origin", "Authorization"],
)
app.add_middleware(SlowAPIMiddleware, limiter=limiter)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/v{major}',
    description='Greet users with a nice message',
    lifespan=lifespan
)


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)


app.mount("/static", StaticFiles(directory="app/static"), "static")