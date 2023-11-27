import logging
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from api.v1 import bookmarks, film_ratings, review_ratings, reviews, views
from core.config import settings
from core.logger import LOGGING
from db import mongo_helper

logging.config.dictConfig(LOGGING)

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    enable_tracing=True,
    integrations=[
        StarletteIntegration(
            transaction_style="endpoint"
        ),
        FastApiIntegration(
            transaction_style="endpoint"
        ),
    ]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_helper.client = AsyncIOMotorClient(settings.mongo_host, settings.mongo_port)
    yield
    await mongo_helper.client.close()


app = FastAPI(
    title=settings.ugc_project_name,
    docs_url="/api/openapi-ugc",
    openapi_url="/api/openapi-ugc.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(bookmarks.router, prefix="/api/v1/bookmarks", tags=["bookmarks"])
app.include_router(film_ratings.router, prefix="/api/v1/film_ratings", tags=["film_ratings"])
app.include_router(review_ratings.router, prefix="/api/v1/review_ratings", tags=["review_ratings"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(views.router, prefix="/api/v1/views", tags=["views"])

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.ugc_fast_api_host, port=settings.ugc_fast_api_port)
