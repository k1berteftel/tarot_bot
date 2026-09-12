import asyncio
import logging
from asyncio import TimeoutError
from typing import Literal
from datetime import datetime, date, timedelta, time

from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram_dialog import BaseDialogManager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.payments.create import check_platega_transaction
from utils.layout.arranging import process_arranging
from database.action_data_class import DataInteraction
from database.build import PostgresBuild
from config_data.config import Config, load_config


logger = logging.getLogger(__name__)


config: Config = load_config()

build = PostgresBuild(config.db.dns)
session: DataInteraction = DataInteraction(build.session())


async def close_all_dialogs(bot: Bot, message: Message, bg_manager: BaseDialogManager, stacks: int = 3):
    for i in range(0, stacks):
        try:
            await bg_manager.done()
        except Exception as e:
            logger.debug(f"done() raised: {e}")
    await asyncio.sleep(2.5)
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        ...


async def wait_for_payment(
        payment_id,
        user_id: int,
        bot: Bot,
        message: Message,
        context: FSMContext,
        bg_manager: BaseDialogManager,
        data: dict,
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
        await asyncio.wait_for(_poll_payment(payment_id, user_id, currency, bot, message, context, bg_manager, data, payment_type, check_interval),
                               timeout=timeout)

    except TimeoutError:
        print(f"Платёж {payment_id} истёк (таймаут)")

    except Exception as e:
        print(f"Ошибка в фоновом ожидании платежа {payment_id}: {e}")


async def _poll_payment(payment_id, user_id: int, currency: int, bot: Bot, message: Message, context: FSMContext, bg_manager: BaseDialogManager, data: dict, payment_type: str, interval: int):
    """
    Цикл опроса статуса платежа.
    Завершается, когда платёж оплачен.
    """
    while True:
        if payment_type in ['card', 'sbp']:
            logger.info('Checking plageta transaction')
            status = await check_platega_transaction(payment_id)
            # status = True
            logger.info(f'Transaction status: {status}')
        else:
            status = False
        if status:
            await close_all_dialogs(bot, message, bg_manager)
            await bot.send_message(
                chat_id=user_id,
                text='✅Оплата прошла успешно\nПожалуйста ожидайте'
            )
            logger.info('Start execute rate')
            await execute_rate(user_id, currency, data, bot, context)
            break
        await asyncio.sleep(interval)


async def execute_rate(user_id: int, currency: int, data: dict, bot: Bot, context: FSMContext):
    rate = data.get('rate')
    # учет по базе данных
    logger.info('Increment static values')
    try:
        await session.add_income(currency)
        await session.increment_static('buys', 1)
        if not data.get('ai_context'):
            await session.increment_static(rate + '_buys', 1)
        else:
            await session.increment_static('question_buys', 1)
        user = await session.get_user(user_id)
        if user.join:
            await session.update_deeplink_earn(user.join, currency)
    except Exception as err:
        logger.error(err)

    logger.info('Create task to arranging')
    task = asyncio.create_task(process_arranging(
        form_data=data,
        user_id=user_id,
        bot=bot,
        context=context,
        messages=data.get('ai_context')
    ))