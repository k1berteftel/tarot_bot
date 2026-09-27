from datetime import datetime, timedelta

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.action_data_class import DataInteraction
from utils.horoscope import send_daily_horoscope


async def wrapper_daily_horoscope(bot: Bot, db: DataInteraction):
    for user in await db.get_users():
        await send_daily_horoscope(bot, user.user_id)


async def wrapper_today(session: DataInteraction):
    for link in await session.get_deeplinks():
        await session.set_deeplink_value(deeplink_id=link.id, today=0)
    await session.set_static_value(today=0)


async def wrapper_week(session: DataInteraction):
    for link in await session.get_deeplinks():
        await session.set_deeplink_value(deeplink_id=link.id, week=0)
    await session.set_static_value(week=0)


async def wrapper_month(session: DataInteraction):
    await session.set_static_value(month=0)


async def start_schedulers(scheduler: AsyncIOScheduler, session: DataInteraction, bot: Bot):
    """Запуск всех планировщиков"""
    # Ежедневный сброс в 00:00
    scheduler.add_job(
        wrapper_today,
        'cron',
        args=[session],
        hour=0,
        minute=0,
        id='reset_daily_profit'
    )
    scheduler.add_job(
        wrapper_week,
        'cron',
        args=[session],
        day_of_week='mon',
        hour=0,
        minute=0,
        id='reset_weekly_profit'
    )
    scheduler.add_job(
        wrapper_month,
        'cron',
        args=[session],
        day=1,
        hour=0,
        minute=0,
        id='reset_monthly_profit'
    )
    scheduler.add_job(
        wrapper_daily_horoscope,
        'cron',
        args=[bot, session],
        hour=8, minute=0,
        id=f'daily_horoscope',
    )

