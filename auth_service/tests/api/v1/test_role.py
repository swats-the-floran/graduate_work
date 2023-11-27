from http import HTTPStatus
from unittest.mock import ANY

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from models.entities import Role, RoleName


@pytest.mark.asyncio
async def test_create_success(delete_roles_for_api, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.post(
            "/api/v1/role/create/", params={"name": "registered"}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == "OK"


@pytest.mark.asyncio
async def test_create_user_without_role() -> None:
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

        async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
            response = await api_client.post(
                "/api/v1/role/create/", params={"name": "test"}, headers={"Authorization": token}
            )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_create_error_already_exists(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.post(
            "/api/v1/role/create/", params={"name": "admin"}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()["detail"] == "Role with name=admin already exists"


@pytest.mark.asyncio
async def test_create_error_unknown_role(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.post(
            "/api/v1/role/create/", params={"name": "admin1"}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_success(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]
    test_role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).first()[0]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.delete(
            f"/api/v1/role/delete/{test_role.id}", params={"role_id": test_role.id}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == "OK"


@pytest.mark.asyncio
async def test_delete_error_forbidden(async_session: AsyncSession) -> None:
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
        test_role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).first()[0]

        response = await api_client.delete(
            f"/api/v1/role/delete/{test_role.id}", params={"role_id": test_role.id}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_delete_error_not_found(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.delete(
            "/api/v1/role/delete/a52c29e9-c45b-47f8-acd0-7de31168a971",
            params={"role_id": "a52c29e9-c45b-47f8-acd0-7de31168a971"},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Role with id=a52c29e9-c45b-47f8-acd0-7de31168a971 not found"


@pytest.mark.asyncio
async def test_roles_one_element_list(delete_roles_for_api, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/role/list/", headers={"Authorization": token})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == [{"id": ANY, "name": "admin"}]


@pytest.mark.asyncio
async def test_roles(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get(
            "/api/v1/role/list/", params={"page_size": 50}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["result"]) == 2


@pytest.mark.asyncio
async def test_list_forbidden() -> None:
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

        response = await api_client.get(
            "/api/v1/role/list/", params={"page_size": 50}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_role_by_name(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/role/", params={"name": "admin"}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == {"id": ANY, "name": "admin"}


@pytest.mark.asyncio
async def test_get_role_by_name_forbidden() -> None:
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

        response = await api_client.get("/api/v1/role/", params={"name": "admin"}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_get_role_error_by_name(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/role/", params={"name": "admin1"}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_role_by_id(async_session: AsyncSession, login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]

    admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).first()[0]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get(
            "/api/v1/role/", params={"role_id": admin_role.id}, headers={"Authorization": token}
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["result"] == {"id": f"{admin_role.id}", "name": "admin"}


@pytest.mark.asyncio
async def test_get_role_error_by_id(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get(
            "/api/v1/role/",
            params={"role_id": "a52c29e9-c45b-47f8-acd0-7de31168a971"},
            headers={"Authorization": token},
        )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Role with id=a52c29e9-c45b-47f8-acd0-7de31168a971 not found"


@pytest.mark.asyncio
async def test_get_role_error_no_id_and_name(login_admin) -> None:
    token = "Bearer " + login_admin["access_token"]

    async with AsyncClient(app=app, base_url="http://test") as api_client, LifespanManager(app):
        response = await api_client.get("/api/v1/role/", params={}, headers={"Authorization": token})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["error"] == "at least one parameter should be provide"
