import datetime
from http import HTTPStatus
from unittest.mock import ANY

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from models.entities import Role, RoleName, User, UserHistory


@pytest.mark.asyncio
async def test_bind_only_admin_role(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()

        response = await api_client.post(
            "/api/v1/user/bind/",
            params={"user_id": user.id, "role_ids": [admin_role.id]},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == "OK"


@pytest.mark.asyncio
async def test_bind_only_admin_and_registered(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
        registered_role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()

        response = await api_client.post(
            "/api/v1/user/bind/",
            params={"user_id": user.id, "role_ids": [admin_role.id, registered_role.id]},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == "OK"


@pytest.mark.asyncio
async def test_bind_empty_roles(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()

        response = await api_client.post(
            "/api/v1/user/bind/", params={"user_id": user.id, "role_ids": []}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Bind empty roles"


@pytest.mark.asyncio
async def test_bind_unknown_role(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()

        response = await api_client.post(
            "/api/v1/user/bind/",
            params={"user_id": user.id, "role_ids": [admin_role.id, "2514c6bd-c341-4362-85f3-0e4e7ce1f7e8"]},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Bind unknown roles with ids=" in response.json()["detail"]


@pytest.mark.asyncio
async def test_bind_user_not_found(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
        await api_client.post(
            "/api/v1/auth/sign_up/",
            params={"email": "test@mail.ru", "password": "Password123"},
        )

        response = await api_client.post(
            "/api/v1/user/bind/",
            params={"user_id": "2514c6bd-c341-4362-85f3-0e4e7ce1f7e8", "role_ids": [admin_role.id]},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "User with id=" in response.json()["detail"]


@pytest.mark.asyncio
async def test_bind_admin_role_forbidden(async_session: AsyncSession) -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
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
            "/api/v1/user/bind/",
            params={"user_id": user.id, "role_ids": [admin_role.id]},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_history(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post("/api/v1/auth/sign_up/", params={"email": "test@mail.ru", "password": "Password123"})
        await api_client.post("/api/v1/auth/sign_in/", params={"email": "test@mail.ru", "password": "Password123"})
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()

        response = await api_client.get(
            "/api/v1/user/history/", params={"user_id": user.id}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["result"]) == 1


@pytest.mark.asyncio
async def test_history_forbidden(async_session: AsyncSession) -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post("/api/v1/auth/sign_up/", params={"email": "test@mail.ru", "password": "Password123"})
        result = await api_client.post(
            "/api/v1/auth/sign_in/", params={"email": "test@mail.ru", "password": "Password123"}
        )
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()
        token = "Bearer " + result.json()["access_token"]

        response = await api_client.get(
            "/api/v1/user/history/", params={"user_id": user.id}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_history_limit_offset(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post("/api/v1/auth/sign_up/", params={"email": "test@mail.ru", "password": "Password123"})
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()
        user.user_history.extend(
            [UserHistory(last_login_datetime=datetime.datetime.now(), device=f"iPhone{i}") for i in range(50)]
        )
        async_session.add(user)
        await async_session.commit()

        response = await api_client.get(
            "/api/v1/user/history/",
            params={"user_id": user.id, "page_size": 9, "page_number": 6},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["result"]) == 5


@pytest.mark.asyncio
async def test_history_empty(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post("/api/v1/auth/sign_up/", params={"email": "test@mail.ru", "password": "Password123"})
        user = (await async_session.execute(select(User).where(User.email == "test@mail.ru"))).scalar()

        response = await api_client.get(
            "/api/v1/user/history/", params={"user_id": user.id}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["result"]) == 0


@pytest.mark.asyncio
async def test_history_user_not_found(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get(
            "/api/v1/user/history/",
            params={"user_id": "2514c6bd-c341-4362-85f3-0e4e7ce1f7e8"},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "User with id=" in response.json()["detail"]


@pytest.mark.asyncio
async def test_users_only_one_list(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/user/all/", headers={"Authorization": token})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == [
        {"id": ANY, "email": "test-admin@mail.ru", "roles": [{"id": ANY, "name": "admin"}]}
    ]


@pytest.mark.asyncio
async def test_users(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    users = []
    for i in range(10):
        users.append(User(email=f"test{i}@mail.ru", password="Password123", roles=[role]))
    async_session.add_all(users)
    await async_session.commit()

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/user/all/", params={"page_size": 2}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == [
        {"id": ANY, "email": "test-admin@mail.ru", "roles": [{"id": ANY, "name": "admin"}]},
        {"id": ANY, "email": "test0@mail.ru", "roles": [{"id": ANY, "name": "registered"}]},
    ]


@pytest.mark.asyncio
async def test_users_forbidden() -> None:
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        await api_client.post("/api/v1/auth/sign_up/", params={"email": "test@mail.ru", "password": "Password123"})
        result = await api_client.post(
            "/api/v1/auth/sign_in/", params={"email": "test@mail.ru", "password": "Password123"}
        )
        token = "Bearer " + result.json()["access_token"]

        response = await api_client.get("/api/v1/user/all/", params={"page_size": 2}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.FORBIDDEN
