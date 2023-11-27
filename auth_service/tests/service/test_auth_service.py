import pytest
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash

from db.exceptions import UserAlreadyExists, UserNotFound
from db.role_repository import RoleRepository
from db.user_repository import UserRepository
from models.entities import RoleName, User
from services.auth_service import AuthService, FakeEmailClient, PasswordNotEqual


@pytest.fixture(scope="function")
def email_client() -> FakeEmailClient:
    return FakeEmailClient()


@pytest.mark.asyncio
async def test_sign_up_user(
    async_session: AsyncSession, user_repo: UserRepository, email_client: FakeEmailClient, redis: Redis
) -> None:
    auth_service = AuthService(user_repo, RoleRepository(async_session), email_client, redis)

    got = await auth_service.sign_up(email="sign_up_user@mail.ru", password="password")

    assert isinstance(got, User)
    assert got.id is not None
    assert got.email == "sign_up_user@mail.ru"
    assert check_password_hash(got.password, "password"), "Пароль должен быть зашифрован"
    assert got.roles[0].name == RoleName.REGISTERED
    assert email_client.send_count == 1


@pytest.mark.asyncio
async def test_sign_up_user_raise_error_because_user_exists_with_email(
    async_session: AsyncSession, user_repo: UserRepository, email_client: FakeEmailClient, redis: Redis
) -> None:
    auth_service = AuthService(user_repo, RoleRepository(async_session), email_client, redis)
    await auth_service.sign_up(email="sign_up_user_raise@mail.ru", password="password")

    with pytest.raises(UserAlreadyExists):
        await auth_service.sign_up(email="sign_up_user_raise@mail.ru", password="newpassword")
    assert email_client.send_count == 1


@pytest.mark.asyncio
async def test_sign_in(
    async_session: AsyncSession, user_repo: UserRepository, email_client: FakeEmailClient, redis: Redis
) -> None:
    auth_service = AuthService(user_repo, RoleRepository(async_session), email_client, redis)
    await auth_service.sign_up(email="sign_in@mail.ru", password="password")

    got = await auth_service.sign_in(email="sign_in@mail.ru", password="password", auth_data={"device": "iPhone13"})

    assert isinstance(got, User)
    assert got.id is not None
    assert got.email == "sign_in@mail.ru"
    assert len(got.user_history) == 1


@pytest.mark.asyncio
async def test_sign_in_raise_exc_because_user_not_found(
    async_session: AsyncSession, user_repo: UserRepository, email_client: FakeEmailClient, redis: Redis
) -> None:
    auth_service = AuthService(user_repo, RoleRepository(async_session), email_client, redis)

    with pytest.raises(UserNotFound):
        await auth_service.sign_in(email="unknown@mail.ru", password="password", auth_data={"device": "iPhone13"})


@pytest.mark.asyncio
async def test_sign_in_raise_exc_because_password_not_equal(
    async_session: AsyncSession, user_repo: UserRepository, email_client: FakeEmailClient, redis: Redis
) -> None:
    auth_service = AuthService(user_repo, RoleRepository(async_session), email_client, redis)
    user = await auth_service.sign_up(email="sign_in_raise@mail.ru", password="password")

    with pytest.raises(PasswordNotEqual):
        await auth_service.sign_in(email="sign_in_raise@mail.ru", password="PaSsWoRd", auth_data={"device": "iPhone13"})
    assert len(user.user_history) == 0


@pytest.mark.asyncio
async def test_change_password(
    async_session: AsyncSession, user_repo: UserRepository, email_client: FakeEmailClient, redis: Redis
) -> None:
    auth_service = AuthService(user_repo, RoleRepository(async_session), email_client, redis)
    user = await auth_service.sign_up(email="change_password@mail.ru", password="password")

    got = await auth_service.change_password(user_id=user.id, old_password="password", new_password="newpassword")

    assert check_password_hash(got.password, "newpassword")
    assert email_client.send_count == 2


@pytest.mark.asyncio
async def test_change_password_raise_exc_because_old_password_not_equal(
    async_session: AsyncSession, user_repo: UserRepository, email_client: FakeEmailClient, redis: Redis
) -> None:
    auth_service = AuthService(user_repo, RoleRepository(async_session), email_client, redis)
    user = await auth_service.sign_up(email="new-test@mail.ru", password="password")

    with pytest.raises(PasswordNotEqual):
        await auth_service.change_password(user_id=user.id, old_password="password123", new_password="newpassword")
    assert email_client.send_count == 1


@pytest.mark.asyncio
async def test_change_password_raise_exc_because_user_not_found(
    async_session: AsyncSession, user_repo: UserRepository, email_client: FakeEmailClient, redis: Redis
) -> None:
    auth_service = AuthService(user_repo, RoleRepository(async_session), email_client, redis)

    with pytest.raises(UserNotFound):
        await auth_service.change_password(
            user_id="217ec052-7455-4588-93d1-b1149b74b1e1",
            old_password="password123",
            new_password="newpassword",
        )
    assert email_client.send_count == 0
