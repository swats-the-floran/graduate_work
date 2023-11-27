import sentry_sdk
import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse, ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.v1 import auth, role, user, social
from core.config import settings
from core.jwt_config import setting_jwt
from db import redis
from extensions.limiter import limiter
from extensions.tracer import configure_tracer


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
    redis.redis = Redis(host=settings.redis_db.host, port=settings.redis_db.port)
    yield
    await redis.redis.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi-auth",
    openapi_url="/api/openapi-auth.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.mount('/static', StaticFiles(directory='static'), name='static')
app.add_middleware(SessionMiddleware, secret_key=settings.middleware_secret_key)
app.add_middleware(
    CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'],
)


@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    if settings.allow_request_id:
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})

    return response


@AuthJWT.load_config
def get_config():
    return setting_jwt


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token["jti"]
    entry = await redis.redis.get(jti)
    return entry


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/healthcheck")
async def health_check() -> str:
    return "OK"


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])
app.include_router(role.router, prefix="/api/v1/role", tags=["role"])
app.include_router(social.router, prefix="/api/v1/social", tags=["social"])

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


if settings.allow_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


if __name__ == "__main__":
    uvicorn.run(app="main:app", host=settings.host, port=settings.port, reload=True)
