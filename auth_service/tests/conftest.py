import asyncio
import datetime

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from db.role_repository import RoleRepository
from db.user_repository import UserRepository
from main import app
from models.entities import Base, Role, RoleName, User, UserHistory


@pytest_asyncio.fixture()
async def redis() -> Redis:
    async with Redis(host=settings.redis_db.host, port=settings.redis_db.port) as redis:
        yield redis


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncEngine:
    async_engine = create_async_engine(settings.db.url, echo=False, future=True)
    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_init(async_engine: AsyncEngine) -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine: AsyncEngine) -> AsyncSession:
    async_session: type[AsyncEngine] = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        yield session

    async with async_engine.begin() as conn:
        await conn.execute(
            text("TRUNCATE {} CASCADE;".format(",".join(table.name for table in reversed(Base.metadata.sorted_tables))))
        )


@pytest_asyncio.fixture(scope="session")
async def fill_db(async_engine: AsyncEngine) -> None:
    async with AsyncSession(bind=async_engine, expire_on_commit=False, autocommit=False, autoflush=False) as session:
        admin_role = Role(name=RoleName.ADMIN)
        registered_role = Role(name=RoleName.REGISTERED)
        test_user = User(
            email="test@mail.ru",
            password=(
                "pbkdf2:sha256:600000"
                "$JcwdB11xzEcn4rgn$e5f02ec4af4781576446d20f30eb95a43b3414fe20c554933574453291ae9e76"
            ),
            user_history=[UserHistory(last_login_datetime=datetime.datetime(2000, 10, 10), device="iPhone13")],
            roles=[registered_role],
        )

        session.add_all([admin_role, registered_role, test_user])
        await session.commit()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def fill_roles_and_create_admin(async_session):
    admin_role = Role(name=RoleName.ADMIN)
    registered_role = Role(name=RoleName.REGISTERED)
    async_session.add_all([admin_role, registered_role])
    await async_session.commit()
    role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
    async_session.add(
        User(
            email="test-admin@mail.ru",
            password=(
                "pbkdf2:sha256:600000"
                "$JcwdB11xzEcn4rgn$e5f02ec4af4781576446d20f30eb95a43b3414fe20c554933574453291ae9e76"
            ),
            user_history=[UserHistory(last_login_datetime=datetime.datetime(2000, 10, 10), device="iPhone13")],
            roles=[role],
        )
    )
    await async_session.commit()


@pytest.fixture()
def role_repo(async_session: AsyncSession) -> RoleRepository:
    return RoleRepository(async_session)


@pytest.fixture()
def user_repo(async_session: AsyncSession) -> UserRepository:
    return UserRepository(async_session)


@pytest_asyncio.fixture()
async def delete_roles_for_api(async_session: AsyncSession):
    registered_role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    if registered_role:
        await async_session.delete(registered_role)
    test_role = (await async_session.execute(select(Role).where(Role.name == RoleName.TEST))).scalar()
    if test_role:
        await async_session.delete(test_role)
    await async_session.commit()


@pytest_asyncio.fixture()
async def delete_roles(async_session: AsyncSession):
    registered_role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    if registered_role:
        await async_session.delete(registered_role)
    admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
    if admin_role:
        await async_session.delete(admin_role)
    await async_session.commit()


@pytest_asyncio.fixture()
async def login_admin():
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.post(
            "/api/v1/auth/sign_in/",
            params={"email": "test-admin@mail.ru", "password": "password"},
        )
    return response.json()
