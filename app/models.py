import datetime
import uuid
from typing import List, Type, Union

from config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


engine = create_async_engine(
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "advt_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(70), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    tokens: Mapped[List["Token"]] = relationship(
        "Token", back_populates="user", cascade="all, delete-orphan"
    )
    advts: Mapped[List["Advt"]] = relationship(
        "Advt", back_populates="owner", cascade="all, delete-orphan"
    )

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "advts": [advt.id for advt in self.advts],
        }


class Token(Base):
    __tablename__ = "token"
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(
        UUID, server_default=func.gen_random_uuid(), unique=True
    )
    creation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("advt_user.id"))
    user: Mapped[User] = relationship(User, back_populates="tokens")

    @property
    def dict(self):
        return {"id": self.id, "token": self.token, "user_id": self.user_id}


class Advt(Base):
    __tablename__ = "advt"
    id: Mapped[int] = mapped_column(primary_key=True)
    header: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=False)
    creation_date: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("advt_user.id"))
    owner: Mapped[User] = relationship(User, back_populates="advts")

    @property
    def dict(self):
        return {
            "id": self.id,
            "header": self.header,
            "description": self.description,
            "creation_date": self.creation_date.isoformat() if self.creation_date else None,
            "user_id": self.user_id,
        }


MODEL_TYPE = Type[Union[User, Token, Advt]]
MODEL = Union[User, Token, Advt]
