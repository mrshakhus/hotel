from contextlib import asynccontextmanager
import sentry_sdk
from prometheus_fastapi_instrumentator import Instrumentator
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.admin.auth import authentication_backend
from app.config import settings
from app.database import engine
from app.bookings.router import router as bookings_router
from app.users.router import router as users_router
from app.hotels.router import router as hotels_router
from app.pages.router import router as pages_router
from app.images.router import router as images_router
from app.csv_files.router import router as csv_files_router
from app.prometheus.router import router as prometheus_router
from app.logger import logger
from fastapi_versioning import VersionedFastAPI

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
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis = await aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield
    await redis.close()

app = FastAPI(lifespan=lifespan)


app.include_router(users_router)
app.include_router(hotels_router)
app.include_router(bookings_router)
app.include_router(pages_router)
app.include_router(images_router)
app.include_router(csv_files_router)
app.include_router(prometheus_router)

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


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     logger.info("Request handling time", extra={
#         "process_time": round(process_time, 4)
#     })
#     response.headers["X-Process-Time"] = str(process_time)
#     return response


app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/v{major}',
    description='Greet users with a nice message',
    # middleware=[
    #     Middleware(SessionMiddleware, secret_key='mysecretkey')
    # ]
)


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)


app.mount("/static", StaticFiles(directory="app/static"), "static")