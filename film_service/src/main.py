import logging
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from api.v1 import films, genres, persons
from core.config import settings
from core.logger import LOGGING
from db import elastic, redis

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
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)
    elastic.es = AsyncElasticsearch(hosts=[settings.elastic.url])
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi-movies",
    openapi_url="/api/openapi-movies.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port)
