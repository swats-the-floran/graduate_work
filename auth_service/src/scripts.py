import asyncio
import logging
from functools import wraps

import typer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from db.postgres import async_database_session
from models.entities import Role, RoleName, User

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def typer_async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@typer_async
async def create_admin(
    email: str = "admin@mail.ru",
    password: str = "Password123",
    first_name: str = "Sirius",
    second_name: str = "Black"
) -> None:
    async with async_database_session() as session:
        admin_role = (await session.execute(select(Role).where(Role.name == RoleName.ADMIN))).scalar()
        user = User(email=email, password=generate_password_hash(password), roles=[admin_role], first_name=first_name, second_name=second_name)
        session.add(user)
        try:
            await session.commit()
            logger.info(f"Администратор успешно добавлен: email={email}; пароль={password}")
        except SQLAlchemyError:
            logger.exception("Ошибка добавления администратора")


if __name__ == "__main__":
    typer.run(create_admin)
