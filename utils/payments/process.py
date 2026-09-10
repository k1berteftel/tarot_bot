import asyncio
import logging
from asyncio import TimeoutError
from typing import Literal
from datetime import datetime, date, timedelta, time

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram_dialog import BaseDialogManager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.payments.create import check_platega_transaction
from utils.layout.arranging import process_arranging
from database.action_data_class import DataInteraction
from config_data.config import Config, load_config


logger = logging.getLogger(__name__)


config: Config = load_config()


async def close_all_dialogs(bg_manager):
    try:
        await bg_manager.done()
    except Exception as e:
        logger.debug(f"done() raised: {e}")
    while True:
        try:
            await bg_manager.done()
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.debug(f"stack empty: {e}")
            break


async def wait_for_payment(
        payment_id,
        user_id: int,
        bot: Bot,
        context: FSMContext,
        bg_manager: BaseDialogManager,
        data: dict,
        session: DataInteraction,
        currency: int,
        payment_type: Literal['card', 'sbp'],
        timeout: int = 60 * 15,
        check_interval: int = 6
):
    """
    Ожидает оплаты в фоне. Завершается при оплате или по таймауту.
    """
    logger.info(f'Start bg checking payment "{payment_id}" - {user_id}')
    try:
        await asyncio.wait_for(_poll_payment(payment_id, user_id, currency, bot, context, bg_manager, data, session,  payment_type, check_interval),
                               timeout=timeout)

    except TimeoutError:
        print(f"Платёж {payment_id} истёк (таймаут)")

    except Exception as e:
        print(f"Ошибка в фоновом ожидании платежа {payment_id}: {e}")


async def _poll_payment(payment_id, user_id: int, currency: int, bot: Bot, context: FSMContext, bg_manager: BaseDialogManager, data: dict, session: DataInteraction,  payment_type: str, interval: int):
    """
    Цикл опроса статуса платежа.
    Завершается, когда платёж оплачен.
    """
    while True:
        if payment_type in ['card', 'sbp']:
            logger.info('Checking plageta transaction')
            status = await check_platega_transaction(payment_id)
            logger.info(f'Transaction status: {status}')
        else:
            status = False
        if status:
            await close_all_dialogs(bg_manager)
            await bot.send_message(
                chat_id=user_id,
                text='✅Оплата прошла успешно'
            )
            logger.info('Start execute rate')
            await execute_rate(user_id, currency, data, bot, context, session)
            break
        await asyncio.sleep(interval)


async def execute_rate(user_id: int, currency: int, data: dict, bot: Bot, context: FSMContext, session: DataInteraction):
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