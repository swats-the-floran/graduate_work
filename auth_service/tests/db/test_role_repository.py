import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.exceptions import RoleAlreadyExists, RoleNotFound
from db.role_repository import RoleRepository
from models.entities import Role, RoleName


@pytest.mark.asyncio
async def test_create_role(role_repo: RoleRepository, delete_roles) -> None:
    got: Role = await role_repo.create(role=Role(name=RoleName.ADMIN))

    assert got.id is not None
    assert got.name == "admin"


@pytest.mark.asyncio
async def test_create_role_error_role_already_exist(role_repo: RoleRepository, delete_roles) -> None:
    await role_repo.create(role=Role(name=RoleName.ADMIN))

    with pytest.raises(RoleAlreadyExists):
        await role_repo.create(role=Role(name=RoleName.ADMIN))


@pytest.mark.asyncio
async def test_delete_role(async_session: AsyncSession, role_repo: RoleRepository, delete_roles) -> None:
    role = await role_repo.create(role=Role(name=RoleName.ADMIN))

    await role_repo.delete(role.id)
    result = (await async_session.execute(select(Role).where(Role.name == RoleName.ADMIN))).all()

    assert len(result) == 0


@pytest.mark.asyncio
async def test_delete_role_error(role_repo: RoleRepository) -> None:
    with pytest.raises(RoleNotFound):
        await role_repo.delete("a52c29e9-c45b-47f8-acd0-7de31168a971")


@pytest.mark.asyncio
async def test_list_role(role_repo: RoleRepository, delete_roles) -> None:
    await role_repo.create(role=Role(name=RoleName.ADMIN))
    await role_repo.create(role=Role(name=RoleName.REGISTERED))

    result = await role_repo.list(limit=10000, offset=0)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_list_role_empty(role_repo: RoleRepository, delete_roles) -> None:
    result = await role_repo.list(limit=10000, offset=0)

    assert len(result) == 0


@pytest.mark.parametrize(
    ("limit", "offset", "expected_len"),
    [
        (1, 0, 1),
        (1, 1, 1),
        (1, 2, 0),
        (2, 0, 2),
        (2, 1, 1),
        (2, 2, 0),
    ],
)
@pytest.mark.asyncio
async def test_list_with_limit_offset(
    role_repo: RoleRepository, limit: int, offset: int, expected_len: int, delete_roles
) -> None:
    await role_repo.create(role=Role(name=RoleName.ADMIN))
    await role_repo.create(role=Role(name=RoleName.REGISTERED))

    got = await role_repo.list(limit=limit, offset=offset)

    assert len(got) == expected_len


@pytest.mark.asyncio
async def test_get_role_by_name(role_repo: RoleRepository, delete_roles) -> None:
    await role_repo.create(role=Role(name=RoleName.ADMIN))

    got = await role_repo.get_role_by_name(name="admin")

    assert got.id is not None
    assert got.name == "admin"


@pytest.mark.asyncio
async def test_get_role_by_name_raise_error(role_repo: RoleRepository, delete_roles) -> None:
    with pytest.raises(RoleNotFound):
        await role_repo.get_role_by_name(name="admin")


@pytest.mark.asyncio
async def test_get_user_by_id(role_repo: RoleRepository, delete_roles) -> None:
    role = await role_repo.create(role=Role(name=RoleName.ADMIN))

    got = await role_repo.get_role_by_id(id_=role.id)

    assert got.id == role.id
    assert got.name == "admin"


@pytest.mark.asyncio
async def test_get_role_by_id_raise_error(role_repo: RoleRepository) -> None:
    with pytest.raises(RoleNotFound):
        await role_repo.get_role_by_id(id_="217ec052-7455-4588-93d1-b1149b74b1e1")


@pytest.mark.asyncio
async def test_get_roles_by_ids(role_repo: RoleRepository, delete_roles) -> None:
    roles = []
    ids = []
    role = await role_repo.create(role=Role(name=RoleName.ADMIN))
    roles.append(role)
    ids.append(role.id)
    role = await role_repo.create(role=Role(name=RoleName.REGISTERED))
    roles.append(role)
    ids.append(role.id)

    got = await role_repo.get_roles_by_ids(role_ids=ids)

    assert len(roles) == len(got)
    for i in range(len(roles)):
        assert roles[i] == got[i]
