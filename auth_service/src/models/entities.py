from __future__ import annotations

import datetime
import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Table, desc, func, Boolean, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class RoleName(str, enum.Enum):
    ADMIN = "admin"
    REGISTERED = "registered"
    TEST = "test"


class SocialNetwork(str, enum.Enum):
    yandex = 'yandex'
    google = 'google'
    vk = 'vk'


users_roles_table = Table(
    "users_roles",
    Base.metadata,
    Column("users_id", ForeignKey("users.id"), nullable=False, primary_key=True),
    Column("roles_id", ForeignKey("roles.id"), nullable=False, primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, nullable=False, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    second_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, unique=False, default=True)

    roles: Mapped[list["Role"]] = relationship(
        secondary=users_roles_table, back_populates="users", lazy="selectin", order_by=lambda: desc(Role.id)
    )
    user_history: Mapped[list["UserHistory"]] = relationship(
        back_populates="user", lazy="selectin", order_by=lambda: desc(UserHistory.id)
    )
    social_account: Mapped[list["SocialAccount"]] = relationship(
        back_populates="user", lazy="selectin", order_by=lambda: desc(SocialAccount.id)
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, password={self.password!r})"

    def as_dict(self) -> dict[str, str | int]:
        return {
            "id": str(self.id),
            "email": self.email,
            "roles": [role.as_dict() for role in self.roles],
            "first_name": self.first_name,
            "second_name": self.second_name,
            "is_active": self.is_active
        }


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Enum(RoleName), default=RoleName.REGISTERED, nullable=False, unique=True)
    users: Mapped[list["User"]] = relationship(secondary=users_roles_table, back_populates="roles")

    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"

    def as_dict(self) -> dict[str, str | int]:
        return {"id": str(self.id), "name": self.name}


class UserHistory(Base):
    __tablename__ = "user_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, nullable=False, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="user_history")
    last_login_datetime: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    device: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return (
            f"UserHistory("
            f"id={self.id!r}, user_id={self.user_id!r}, "
            f"last_login_datetime={self.last_login_datetime!r}, device={self.device!r})"
        )

    def as_dict(self) -> dict[str, str | int]:
        return {
            "id": str(self.id),
            "last_login_datetime": str(self.last_login_datetime),
            "device": self.device,
        }


class SocialAccount(Base):
    __tablename__ = "social_account"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, nullable=False, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="social_account")

    social_id: Mapped[str] = mapped_column(String, nullable=False)
    social_name: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (UniqueConstraint('social_id', 'social_name', name='social_pk'), )

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'

