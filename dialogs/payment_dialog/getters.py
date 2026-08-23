import asyncio

from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput
from nats.js import JetStreamContext

from utils.payments.create import (get_yookassa_url)
from utils.payments.process import wait_for_payment
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import startSG, PaymentSG

from constants import RATES, RATES_DESCRIPTION


config: Config = load_config()


async def menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    if dialog_manager.start_data:
        dialog_manager.dialog_data.update(dialog_manager.start_data)
        dialog_manager.start_data.clear()
    rate = dialog_manager.dialog_data.get('rate')
    cost = dialog_manager.dialog_data.get('cost')
    text = f'<b>Тариф: </b> Расклад <em>"{RATES.get(rate)}"</em>\n<b>Стоимость: </b> {cost}₽'

    return {'text': text}


async def payment_choose(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    state: FSMContext = dialog_manager.dialog_data.get('state')
    rate = dialog_manager.dialog_data.get('rate')
    cost = dialog_manager.dialog_data.get('cost')
    payment_type = clb.data.split('_')[0]

    if payment_type == 'card':
        payment = await get_yookassa_url(cost, RATES_DESCRIPTION.get(rate))
        task = asyncio.create_task(
            wait_for_payment(
                payment_id=payment.get('id'),
                user_id=clb.from_user.id,
                bot=clb.bot,
                context=state,
                data=dialog_manager.dialog_data,
                session=session,
                currency=cost,
                payment_type='card',
            )
        )
        for active_task in asyncio.all_tasks():
            if active_task.get_name() == f'process_payment_{clb.from_user.id}':
                active_task.cancel()
    else:
        pass
    dialog_manager.dialog_data['url'] = payment.get('url')
    await dialog_manager.switch_to(PaymentSG.process_payment)


async def process_payment_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    amount = dialog_manager.dialog_data.get('amount')
    usdt = dialog_manager.dialog_data.get('usdt')
    url = dialog_manager.dialog_data.get('url')
    text = f'<blockquote> - Сумма к оплате: {amount}₽ ({usdt}$)</blockquote>'
    return {
        'text': text,
        'url': url
    }


async def close_payment(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    name = f'process_payment_{clb.from_user.id}'
    for task in asyncio.all_tasks():
        if task.get_name() == name:
            task.cancel()
    await dialog_manager.switch_to(PaymentSG.menu)