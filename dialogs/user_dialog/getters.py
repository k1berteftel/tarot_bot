import asyncio
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, ContentType
from aiogram.enums import ChatAction
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from utils.card_reading import get_one_card
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import startSG, FormSG


config: Config = load_config()


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admin = False
    admins = [*config.bot.admin_ids]
    admins.extend([admin.user_id for admin in await session.get_admins()])
    if event_from_user.id in admins:
        admin = True
    media = MediaAttachment(
        type=ContentType.PHOTO,
        path='img.png'
    )
    return {
        'media': media,
        'admin': admin
    }


async def choose_rate(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    rate = clb.data.split('_')[0]
    data = {
        'rate': rate
    }
    await dialog_manager.start(FormSG.get_name, data=data)


async def one_card(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(clb.from_user.id)
    if user.augury and user.augury > (datetime.now() - timedelta(days=1)):
        await clb.answer('❗️Бесплатное гадание доступно раз в сутки, пожалуйста попробуйте позже')
        return
    bot: Bot = dialog_manager.middleware_data.get('bot')
    try:
        await bot.send_chat_action(
            chat_id=clb.from_user.id,
            action=ChatAction.TYPING
        )
    except Exception:
        ...
    done_time = datetime.now()
    text = get_one_card()
    await asyncio.sleep(2)
    try:
        await clb.message.answer(text)
    except Exception:
        ...
    await session.set_user_augury(clb.from_user.id, done_time)



