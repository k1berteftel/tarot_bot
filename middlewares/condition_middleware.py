import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, User
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.horoscope import send_daily_horoscope
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config

config: Config = load_config()
logger = logging.getLogger(__name__)


class RemindMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user: User = data.get('event_from_user')

        if user is None:
            return await handler(event, data)

        session: DataInteraction = data.get('session')
        await session.set_activity(user_id=user.id)
        scheduler: AsyncIOScheduler = data.get('scheduler')
        job = scheduler.get_job(job_id=f'horoscope_{user.id}')

        result = await handler(event, data)

        bot: Bot = data.get('bot')
        if not job:
            try:
                scheduler.add_job(
                    send_daily_horoscope,
                    'cron',
                    args=[bot, user.id],
                    hour=8,
                    minute=0,
                    id=f'horoscope_{user.id}'
                )
            except Exception:
                ...
        return result
