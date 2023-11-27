import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.exceptions import UserAlreadyExists, UserNotFound
from db.user_repository import UserRepository
from models.entities import Role, RoleName, User, UserHistory


@pytest.mark.asyncio
async def test_create_user(async_session: AsyncSession, user_repo: UserRepository) -> None:
    role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).first()[0]

    got: User = await user_repo.create(user=User(email="test@mail.ru", password="password", roles=[role]))

    assert got.id is not None
    assert got.email == "test@mail.ru"
    assert got.password == "password"
    assert got.roles[0].name == RoleName.REGISTERED
    assert got.user_history == []


@pytest.mark.asyncio
async def test_create_user_raise_error_if_email_already_exist(
    async_session: AsyncSession, user_repo: UserRepository
) -> None:
    role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).first()[0]
    await user_repo.create(user=User(email="test@mail.ru", password="password", roles=[role]))

    with pytest.raises(UserAlreadyExists):
        await user_repo.create(user=User(email="test@mail.ru", password="password", roles=[role]))


@pytest.mark.asyncio
async def test_update_user_password(async_session: AsyncSession, user_repo: UserRepository) -> None:
    role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).first()[0]
    user = await user_repo.create(user=User(email="test@mail.ru", password="password", roles=[role]))
    user.password = "new_password"

    got = await user_repo.update(user=user)

    assert got.id == user.id
    assert got.email == "test@mail.ru"
    assert got.password == "new_password"
    assert got.roles[0].name == RoleName.REGISTERED
    assert got.user_history == []


@pytest.mark.asyncio
async def test_update_user_email(async_session: AsyncSession, user_repo: UserRepository) -> None:
    role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).first()[0]
    user = await user_repo.create(user=User(email="test@mail.ru", password="password", roles=[role]))
    user.email = "new_test@mail.ru"

    got = await user_repo.update(user=user)

    assert got.id == user.id
    assert got.email == "new_test@mail.ru"
    assert got.password == "password"
    assert got.roles[0].name == RoleName.REGISTERED
    assert got.user_history == []


@pytest.mark.asyncio
async def test_update_user_add_new_role(async_session: AsyncSession, user_repo: UserRepository) -> None:
    registered_role = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    admin_role = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
    user = await user_repo.create(user=User(email="test@mail.ru", password="password", roles=[registered_role]))
    user.roles.append(admin_role)

    got = await user_repo.update(user=user)

    assert got.id == user.id
    assert got.email == "test@mail.ru"
    assert got.password == "password"
    assert RoleName.REGISTERED in [role.name for role in got.roles]
    assert RoleName.ADMIN in [role.name for role in got.roles]
    assert got.user_history == []


@pytest.mark.asyncio
async def test_update_user_delete_registered_role(async_session: AsyncSession, user_repo: UserRepository) -> None:
    registered = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    admin = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
    user = await user_repo.create(user=User(email="test@mail.ru", password="password", roles=[registered, admin]))
    user.roles = [admin]

    got = await user_repo.update(user=user)

    assert got.id == user.id
    assert got.email == "test@mail.ru"
    assert got.password == "password"
    assert len(got.roles) == 1
    assert got.roles[0].name == RoleName.ADMIN
    assert got.user_history == []


@pytest.mark.asyncio
async def test_update_user_with_user_history(async_session: AsyncSession, user_repo: UserRepository) -> None:
    registered = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    user = await user_repo.create(user=User(email="test0@mail.ru", password="password", roles=[registered]))
    histories = []
    for index in range(1, 13):
        history = UserHistory(last_login_datetime=datetime.datetime(2000, 1, index), device=f"iPhone{index}")
        histories.append(history)
    user.user_history.extend(histories)

    got = await user_repo.update(user=user)

    assert len(got.user_history) == 12


@pytest.mark.asyncio
async def test_list(async_session: AsyncSession, user_repo: UserRepository) -> None:
    registered = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    for i in range(3):
        await user_repo.create(user=User(email=f"test{i}@mail.ru", password="password", roles=[registered]))

    got = await user_repo.list(limit=10000, offset=0)

    assert len(got) == 4
    for i in range(1, len(got)):
        assert got[i].roles[0].name == RoleName.REGISTERED


@pytest.mark.asyncio
async def test_list_admin(user_repo: UserRepository) -> None:
    got = await user_repo.list(limit=10000, offset=0)

    assert len(got) == 1


@pytest.mark.parametrize("count_len", [15])
@pytest.mark.parametrize(
    ("limit", "offset", "expected_len"),
    [
        (10, 0, 10),
        (10, 10, 6),
        (10, 20, 0),
        (20, 0, 16),
        (20, 20, 0),
        (5, 0, 5),
        (5, 5, 5),
        (5, 10, 5),
        (5, 15, 1),
    ],
)
@pytest.mark.asyncio
async def test_list_with_limit_offset(
    async_session: AsyncSession,
    user_repo: UserRepository,
    limit: int,
    offset: int,
    count_len: int,
    expected_len: int,
) -> None:
    registered = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    for i in range(count_len):
        await user_repo.create(user=User(email=f"test{i}@mail.ru", password="password", roles=[registered]))

    got = await user_repo.list(limit=limit, offset=offset)

    assert len(got) == expected_len


@pytest.mark.asyncio
async def test_get_user_by_email(async_session: AsyncSession, user_repo: UserRepository) -> None:
    registered = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    for i in range(3):
        await user_repo.create(user=User(email=f"test{i}@mail.ru", password="password", roles=[registered]))

    got = await user_repo.get_user_by_email(email="test0@mail.ru")

    assert got.email == "test0@mail.ru"
    assert got.roles[0].name == RoleName.REGISTERED


@pytest.mark.asyncio
async def test_get_user_by_email_raise_error(user_repo: UserRepository) -> None:
    with pytest.raises(UserNotFound):
        await user_repo.get_user_by_email(email="test0@mail.ru")


@pytest.mark.asyncio
async def test_get_user_by_id(async_session: AsyncSession, user_repo: UserRepository) -> None:
    registered = (await async_session.execute(select(Role).where(Role.name == RoleName.REGISTERED))).scalar()
    users = []
    for i in range(3):
        user = await user_repo.create(user=User(email=f"test{i}@mail.ru", password="password", roles=[registered]))
        users.append(user)

    got = await user_repo.get_user_by_id(id_=users[0].id)

    assert got.id == users[0].id
    assert got.email == "test0@mail.ru"
    assert got.roles[0].name == RoleName.REGISTERED


@pytest.mark.asyncio
async def test_get_user_by_id_raise_error(user_repo: UserRepository) -> None:
    with pytest.raises(UserNotFound):
        await user_repo.get_user_by_id(id_="217ec052-7455-4588-93d1-b1149b74b1e1")
