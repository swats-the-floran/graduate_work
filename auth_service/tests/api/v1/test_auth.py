from http import HTTPStatus
from unittest.mock import ANY

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from models.entities import Role, RoleName, User


@pytest_asyncio.fixture()
async def user_test(async_session: AsyncSession):
    role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    async_session.add(User(email="test-client@mail.ru", password="password", roles=[role]))
    await async_session.commit()


@pytest.mark.asyncio
async def test_sign_up_success() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test-client@mail.ru", "password": "Password123"},
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == "OK"


@pytest.mark.asyncio
async def test_sign_up_conflic_because_user_already_exists(user_test) -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test-client@mail.ru", "password": "Password123"},
        )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()["detail"] == "User with email=test-client@mail.ru already exists"


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("test", "Password123"),
        ("test@mail.ru", ""),  # Нет пароля
        ("test@mail.ru", "pass"),  # Пароль меньше 8 символов
        ("test@mail.ru", "password"),  # Пароль не имеет большой буквы
        ("test@mail.ru", "Password"),  # Пароль не имеет цифры
    ],
)
@pytest.mark.asyncio
async def test_sign_up_validate_error(email: str, password: str) -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": email, "password": password},
        )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_sign_in() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )

        response = await api_client.post(
            "/api/v1/auth/sign_in/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"access_token": ANY, "refresh_token": ANY}


@pytest.mark.asyncio
async def test_sign_in_not_found_user() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.post(
            "/api/v1/auth/sign_in/",
            params={"email": "test-unknown@mail.ru", "password": "Password123"},
        )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "User with email=test-unknown@mail.ru not found"


@pytest.mark.asyncio
async def test_sign_in_incorrect_password() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )

        response = await api_client.post(
            "/api/v1/auth/sign_in/",
            params={"email": "test@mail.ru", "password": "olololololololol"},
        )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["detail"] == "Passwords not equal"


@pytest.mark.asyncio
async def test_change_password(async_session: AsyncSession) -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        response_login = await api_client.post(
            "/api/v1/auth/sign_in/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()
        token = "Bearer " + response_login.json()["access_token"]

        response = await api_client.post(
            "/api/v1/auth/change_password/",
            params={"user_id": user.id, "old": "Password123", "new": "NewPassword123"},
            headers={"Authorization": token},
        )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == "OK"


@pytest.mark.asyncio
async def test_change_password_without_token(async_session: AsyncSession) -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()

        response = await api_client.post(
            "/api/v1/auth/change_password/",
            params={"user_id": user.id, "old": "Password123", "new": "NewPassword123"},
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_change_password_by_admin(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()

        response = await api_client.post(
            "/api/v1/auth/change_password/",
            params={"user_id": user.id, "old": "Password123", "new": "NewPassword123"},
            headers={"Authorization": token},
        )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == "OK"


@pytest.mark.asyncio
async def test_change_password_user_not_found(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )

        response = await api_client.post(
            "/api/v1/auth/change_password/",
            params={"user_id": "04c1ddae-3a09-4af0-88f2-fe6c09194a26", "old": "Password123", "new": "NewPassword123"},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "User with id=04c1ddae-3a09-4af0-88f2-fe6c09194a26 not found"


@pytest.mark.asyncio
async def test_change_password_old_password_not_equal(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()

        response = await api_client.post(
            "/api/v1/auth/change_password/",
            params={"user_id": user.id, "old": "Password1234567", "new": "NewPassword123"},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["detail"] == "Old password not equal"


@pytest.mark.asyncio
async def test_refresh_success() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        response_login = await api_client.post(
            "/api/v1/auth/sign_in/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        token = "Bearer " + response_login.json()["refresh_token"]

        response = await api_client.post("/api/v1/auth/refresh/", params={}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"refresh_token": ANY}


@pytest.mark.asyncio
async def test_refresh_access_token_error() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        response_login = await api_client.post(
            "/api/v1/auth/sign_in/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        token = "Bearer " + response_login.json()["access_token"]

        response = await api_client.post("/api/v1/auth/refresh/", params={}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_refresh_old_token() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        response_login = await api_client.post(
            "/api/v1/auth/sign_in/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        token = "Bearer " + response_login.json()["refresh_token"]

        await api_client.delete("/api/v1/auth/logout/", params={}, headers={"Authorization": token})

        response = await api_client.post("/api/v1/auth/refresh/", params={}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_logout() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        response_login = await api_client.post(
            "/api/v1/auth/sign_in/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        token = "Bearer " + response_login.json()["refresh_token"]

        response = await api_client.delete("/api/v1/auth/logout/", params={}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.OK
