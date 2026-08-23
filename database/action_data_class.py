import datetime

from sqlalchemy import select, insert, update, column, text, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.model import (UsersTable, DeeplinksTable, OneTimeLinksIdsTable, AdminsTable, PricesTable, StaticTable,
                            OpTable)
from constants import DEFAULT_RATE_PRICES


async def setup_tables(sessions: async_sessionmaker):
    async with sessions() as session:
        if not await session.scalar(select(PricesTable)):
            for rate, price in DEFAULT_RATE_PRICES.items():
                await session.execute(insert(PricesTable).values({
                    'rate_name': rate,
                    'price': price
                }))
        if not await session.scalar(select(StaticTable)):
            await session.execute(insert(StaticTable).values())

        await session.commit()


class DataInteraction():
    def __init__(self, session: async_sessionmaker):
        self._sessions = session

    async def check_user(self, user_id: int) -> bool:
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.user_id == user_id))
        return True if result else False

    async def add_user(self, user_id: int, username: str, name: str):
        if await self.check_user(user_id):
            return
        async with self._sessions() as session:
            await session.execute(insert(UsersTable).values(
                user_id=user_id,
                username=username,
                name=name,
            ))
            await session.commit()

    async def add_entry(self, link: str):
        async with self._sessions() as session:
            await session.execute(update(DeeplinksTable).where(DeeplinksTable.link == link).values(
                entry=DeeplinksTable.entry+1
            ))
            await session.commit()

    async def add_deeplink(self, link: str):
        async with self._sessions() as session:
            await session.execute(insert(DeeplinksTable).values(
                link=link
            ))
            await session.commit()

    async def add_link(self, link: str):
        async with self._sessions() as session:
            await session.execute(insert(OneTimeLinksIdsTable).values(
                link=link
            ))
            await session.commit()

    async def add_admin(self, user_id: int, name: str):
        async with self._sessions() as session:
            await session.execute(insert(AdminsTable).values(
                user_id=user_id,
                name=name
            ))
            await session.commit()

    async def get_users(self):
        async with self._sessions() as session:
            result = await session.scalars(select(UsersTable))
        return result.fetchall()

    async def get_user(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.user_id == user_id))
        return result

    async def get_user_by_username(self, username: str):
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.username == username))
        return result

    async def add_op(self, chat_id: int, name: str, link: str):
        async with self._sessions() as session:
            await session.execute(insert(OpTable).values(
                chat_id=chat_id,
                name=name,
                link=link
            ))
            await session.commit()

    async def get_links(self):
        async with self._sessions() as session:
            result = await session.scalars(select(OneTimeLinksIdsTable))
        return result.fetchall()

    async def get_admins(self):
        async with self._sessions() as session:
            result = await session.scalars(select(AdminsTable))
        return result.fetchall()

    async def get_deeplinks(self):
        async with self._sessions() as session:
            result = await session.scalars(select(DeeplinksTable))
        return result.fetchall()

    async def get_rates(self):
        async with self._sessions() as session:
            result = await session.scalals(select(PricesTable))
        return result

    async def get_rate_price(self, rate_name: str) -> int:
        async with self._sessions() as session:
            result = await session.scalar(select(PricesTable).where(PricesTable.rate_name == rate_name))
        return result.price if result else None

    async def get_static(self):
        async with self._sessions() as session:
            result = await session.scalar(select(StaticTable))
        return result

    async def get_op(self):
        async with self._sessions() as session:
            result = await session.scalars(select(OpTable))
        return result.fetchall()

    async def get_op_by_chat_id(self, chat_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(OpTable).where(OpTable.chat_id == chat_id))
        return result

    async def increment_static(self, column: str, value: any):
        async with self._sessions() as session:
            await session.execute(update(StaticTable).values(
                {
                    column: getattr(StaticTable, column) + value
                }
            ))
            await session.commit()

    async def set_activity(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                activity=datetime.datetime.today()
            ))
            await session.commit()

    async def set_active(self, user_id: int, active: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                active=active
            ))
            await session.commit()

    async def set_user_augury(self, user_id: int, done_time: datetime.datetime):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                augury=done_time
            ))
            await session.commit()

    async def set_rate_price(self, rate_name: str, price: float | int):
        async with self._sessions() as session:
            await session.execute(update(PricesTable).values(
                {
                    rate_name: price
                }
            ))
            await session.commit()

    async def set_button_link(self, chat_id: int, link: str):
        async with self._sessions() as session:
            await session.execute(update(OpTable).where(OpTable.chat_id == chat_id).values(
                link=link
            ))
            await session.commit()

    async def set_user_op(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                op=True
            ))
            await session.commit()

    async def update_op_entry(self, op_id: int):
        async with self._sessions() as session:
            await session.execute(update(OpTable).where(OpTable.id == op_id).values(
                entry=OpTable.entry + 1
            ))
            await session.commit()

    async def del_deeplink(self, link: str):
        async with self._sessions() as session:
            await session.execute(delete(DeeplinksTable).where(DeeplinksTable.link == link))
            await session.commit()

    async def del_link(self, link_id: str):
        async with self._sessions() as session:
            await session.execute(delete(OneTimeLinksIdsTable).where(OneTimeLinksIdsTable.link == link_id))
            await session.commit()

    async def del_admin(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(delete(AdminsTable).where(AdminsTable.user_id == user_id))
            await session.commit()

    async def del_op_channel(self, chat_id: int):
        async with self._sessions() as session:
            await session.execute(delete(OpTable).where(OpTable.chat_id == chat_id))
            await session.commit()

