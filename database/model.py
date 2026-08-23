import datetime

from sqlalchemy import BigInteger, VARCHAR, ForeignKey, DateTime, Boolean, Column, Integer, String, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UsersTable(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(VARCHAR)
    name: Mapped[str] = mapped_column(VARCHAR)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    active: Mapped[int] = mapped_column(Integer, default=1)
    activity: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    entry: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=False), default=func.now())
    augury: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=False), default=None, nullable=True)

    op: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)


class DeeplinksTable(Base):
    __tablename__ = 'deeplinks'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    link: Mapped[str] = mapped_column(VARCHAR)
    entry: Mapped[int] = mapped_column(BigInteger, default=0)


class AdminsTable(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(VARCHAR)


class OneTimeLinksIdsTable(Base):
    __tablename__ = 'links'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    link: Mapped[str] = mapped_column(VARCHAR)


class OpTable(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    chat_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(VARCHAR)
    link: Mapped[str] = mapped_column(VARCHAR)
    entry: Mapped[int] = mapped_column(Integer, default=0)


class PricesTable(Base):
    __tablename__ = 'prices'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    rate_name: Mapped[str] = mapped_column(VARCHAR)
    price: Mapped[float] = mapped_column(Float)  # стоимость в рублях


class StaticTable(Base):
    __tablename__ = 'static'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    sum: Mapped[int] = mapped_column(Integer, default=0)
    buys: Mapped[int] = mapped_column(Integer, default=0)

    relation_buys: Mapped[int] = mapped_column(Integer, default=0)
    old_buys: Mapped[int] = mapped_column(Integer, default=0)
    future_buys: Mapped[int] = mapped_column(Integer, default=0)

    question_buys: Mapped[int] = mapped_column(Integer, default=0)



