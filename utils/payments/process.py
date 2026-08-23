import asyncio
from asyncio import TimeoutError
from typing import Literal
from datetime import datetime, date, timedelta, time

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.payments.create import check_yookassa_payment
from utils.layout.arranging import process_arranging
from database.action_data_class import DataInteraction
from config_data.config import Config, load_config


config: Config = load_config()


async def wait_for_payment(
        payment_id,
        user_id: int,
        bot: Bot,
        context: FSMContext,
        data: dict,
        session: DataInteraction,
        currency: int,
        payment_type: Literal['card'],
        timeout: int = 60 * 15,
        check_interval: int = 6
):
    """
    Ожидает оплаты в фоне. Завершается при оплате или по таймауту.
    """
    try:
        await asyncio.wait_for(_poll_payment(payment_id, user_id, currency, bot, context, data, session,  payment_type, check_interval),
                               timeout=timeout)

    except TimeoutError:
        print(f"Платёж {payment_id} истёк (таймаут)")

    except Exception as e:
        print(f"Ошибка в фоновом ожидании платежа {payment_id}: {e}")


async def _poll_payment(payment_id, user_id: int, currency: int, bot: Bot, context: FSMContext, data: dict, session: DataInteraction,  payment_type: str, interval: int):
    """
    Цикл опроса статуса платежа.
    Завершается, когда платёж оплачен.
    """
    while True:
        if payment_type == 'card':
            status = await check_yookassa_payment(payment_id)
        else:
            status = False
        if status:
            await bot.send_message(
                chat_id=user_id,
                text='✅Оплата прошла успешно'
            )
            await execute_rate(user_id, currency, data, payment_type, bot, context, session)
            break
        await asyncio.sleep(interval)


async def execute_rate(user_id: int, currency: int, data: dict, payment_type: str, bot: Bot, context: FSMContext, session: DataInteraction):
    rate = data.get('rate')
    # учет по базе данных
    await session.increment_static('sum', currency)
    await session.increment_static('buys', 1)
    await session.increment_static(rate + '_buys', 1)

    task = asyncio.create_task(process_arranging(
        form_data=data,
        user_id=user_id,
        bot=bot,
        context=context,
        messages=data.get('ai_context')
    ))