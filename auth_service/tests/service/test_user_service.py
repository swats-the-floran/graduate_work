import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.exceptions import UserNotFound
from db.role_repository import RoleRepository
from db.user_repository import UserRepository
from models.entities import Role, RoleName, User, UserHistory
from services.exceptions import BindEmptyRoles, BindUnknownRoles
from services.user_service import UserService


@pytest.mark.asyncio
async def test_bind_user_only_admin_role(
    async_session: AsyncSession,
    user_repo: UserRepository,
) -> None:
    user_service = UserService(user_repo, RoleRepository(async_session))
    user = await user_repo.create(user=User(email="bind_user_only_admin_role@mail.ru", password="password"))
    admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()

    got = await user_service.bind(user.id, [admin_role.id])

    assert len(got.roles) == 1
    assert got.roles[0].name == RoleName.ADMIN


@pytest.mark.asyncio
async def test_bind_user_rebind_registered(
    async_session: AsyncSession,
    user_repo: UserRepository,
) -> None:
    user_service = UserService(user_repo, RoleRepository(async_session))
    user = await user_repo.create(user=User(email="bind_user_rebind@mail.ru", password="password"))
    registered_role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()

    got = await user_service.bind(user.id, [registered_role.id])

    assert len(got.roles) == 1
    assert got.roles[0].name == RoleName.REGISTERED


@pytest.mark.asyncio
async def test_bind_user_more_roles(
    async_session: AsyncSession,
    user_repo: UserRepository,
) -> None:
    user_service = UserService(user_repo, RoleRepository(async_session))
    user = await user_repo.create(user=User(email="bind_user_more_roles@mail.ru", password="password"))
    admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
    registered_role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()

    got = await user_service.bind(user.id, [admin_role.id, registered_role.id])

    assert len(got.roles) == 2


@pytest.mark.asyncio
async def test_bind_raise_exc_if_role_ids_not_exists(
    async_session: AsyncSession,
    user_repo: UserRepository,
) -> None:
    user_service = UserService(user_repo, RoleRepository(async_session))
    user = await user_repo.create(user=User(email="bind_raise_exc@mail.ru", password="password"))

    with pytest.raises(BindEmptyRoles):
        await user_service.bind(user.id, ["217ec052-7455-4588-93d1-b1149b74b1e1"])


@pytest.mark.asyncio
async def test_bind_raise_exc_if_found_roles_not_equal_len_role_ids_from_params(
    async_session: AsyncSession,
    user_repo: UserRepository,
) -> None:
    user_service = UserService(user_repo, RoleRepository(async_session))
    user = await user_repo.create(user=User(email="bind_raise@mail.ru", password="password"))
    admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()

    with pytest.raises(BindUnknownRoles):
        await user_service.bind(user.id, ["217ec052-7455-4588-93d1-b1149b74b1e1", admin_role.id])


@pytest.mark.asyncio
async def test_bind_raise_exc_if_user_not_found(
    async_session: AsyncSession,
    user_repo: UserRepository,
) -> None:
    user_service = UserService(user_repo, RoleRepository(async_session))

    with pytest.raises(UserNotFound):
        await user_service.bind("217ec052-7455-4588-93d1-b1149b74b1e1", ["217ec052-7455-4588-93d1-b1149b74b1e1"])


@pytest.mark.asyncio
async def test_history(
    async_session: AsyncSession,
    user_repo: UserRepository,
) -> None:
    user_service = UserService(user_repo, RoleRepository(async_session))
    user_history = UserHistory(last_login_datetime=datetime.datetime.now(), device="iPhone11")
    user = await user_repo.create(user=User(email="histor@mail.ru", password="password", user_history=[user_history]))

    got = await user_service.history(user.id, limit=1000, offset=0)

    assert got[0].device == "iPhone11"


@pytest.mark.parametrize(
    ("limit", "offset", "count_histories", "expected_len"),
    [
        (1000, 0, 13, 13),
        (10, 0, 13, 10),
        (10, 10, 13, 3),
        (10, 20, 13, 0),
    ],
)
@pytest.mark.asyncio
async def test_history_with_limit_offset(
    async_session: AsyncSession,
    user_repo: UserRepository,
    limit: int,
    offset: int,
    count_histories: int,
    expected_len: int,
) -> None:
    user_service = UserService(user_repo, RoleRepository(async_session))
    user_histories = [
        UserHistory(last_login_datetime=datetime.datetime.now(), device=f"iPhone{i}") for i in range(0, count_histories)
    ]
    user = await user_repo.create(
        user=User(
            email=f"history{expected_len}@mail.ru",
            password="password",
            user_history=user_histories,
        ),
    )

    got = await user_service.history(user.id, limit=limit, offset=offset)

    assert len(got) == expected_len


@pytest.mark.parametrize(("limit", "offset", "expected"), [(5, 0, 5), (5, 5, 5), (5, 10, 1)])
@pytest.mark.asyncio
async def test_all(
    async_session: AsyncSession,
    user_repo: UserRepository,
    limit: int,
    offset: int,
    expected: int,
) -> None:
    user_service = UserService(user_repo, RoleRepository(async_session))
    user_histories = [
        UserHistory(last_login_datetime=datetime.datetime.now(), device=f"iPhone{i}") for i in range(0, 2)
    ]
    role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    for i in range(10):
        await user_repo.create(
            user=User(
                email=f"history{i}@mail.ru",
                password="password",
                user_history=user_histories,
                roles=[role],
            ),
        )

    got = await user_service.all(limit=limit, offset=offset)

    assert len(got) == expected
