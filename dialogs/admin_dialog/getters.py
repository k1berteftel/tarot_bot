import os
import datetime

from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.build_ids import get_random_id
from utils.schedulers import send_messages
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import startSG, adminSG


async def get_static(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    users = await session.get_users()
    active = 0
    entry = {
        'today': 0,
        'yesterday': 0,
        '2_day_ago': 0
    }
    activity = 0
    for user in users:
        if user.active:
            active += 1
        for day in range(0, 3):
            #print(user.entry.date(), (datetime.datetime.today() - datetime.timedelta(days=day)).date())
            if user.entry.date() == (datetime.datetime.today() - datetime.timedelta(days=day)).date():
                if day == 0:
                    entry['today'] = entry.get('today') + 1
                elif day == 1:
                    entry['yesterday'] = entry.get('yesterday') + 1
                else:
                    entry['2_day_ago'] = entry.get('2_day_ago') + 1
        if user.activity.timestamp() > (datetime.datetime.today() - datetime.timedelta(days=1)).timestamp():
            activity += 1

    static = await session.get_static()
    text = (f'<b>Статистика на {datetime.datetime.today().strftime("%d-%m-%Y")}</b>\n\nВсего пользователей: {len(users)}'
            f'\n - Активные пользователи(не заблокировали бота): {active}\n - Пользователей заблокировали '
            f'бота: {len(users) - active}\n - Провзаимодействовали с ботом за последние 24 часа: {activity}\n\n'
            f'<b>Прирост аудитории:</b>\n - За сегодня: +{entry.get("today")}\n - Вчера: +{entry.get("yesterday")}'
            f'\n - Позавчера: + {entry.get("2_day_ago")}\n\n<b>Доходы/Расклады:</b>'
            f' - Сумма покупок: {static.sum}\n - Кол-во покупок: {static.buys}\n - Покупок "Диагностика отношений": '
            f'{static.relation_buys}\n - Покупок "Вернется ли бывший": {static.old_buys}\n - Покупок '
            f'"Будущее на 3 месяца": {static.future_buys}\n - Допродаж: {static.question_buys}')
    await clb.message.answer(text=text)


async def get_users_txt(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    users = await session.get_users()
    with open('users.txt', 'a+') as file:
        for user in users:
            file.write(f'{user.user_id}\n')
    await clb.message.answer_document(
        document=FSInputFile(path='users.txt')
    )
    try:
        os.remove('users.txt')
    except Exception:
        ...


async def deeplink_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    links = await session.get_deeplinks()
    text = ''
    for link in links:
        text += f'https://t.me/bot?start={link.link}: {link.entry}\n'  # Получить ссылку на бота и поменять
    return {'links': text}


async def add_deeplink(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.add_deeplink(get_random_id())
    await dialog_manager.switch_to(adminSG.deeplink_menu)


async def del_deeplink(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_deeplink(item_id)
    await clb.answer('Ссылка была успешно удаленна')
    await dialog_manager.switch_to(adminSG.deeplink_menu)


async def del_deeplink_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    links = await session.get_deeplinks()
    buttons = []
    for link in links:
        buttons.append((f'{link.link}: {link.entry}', link.link))
    return {'items': buttons}


async def del_admin(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_admin(int(item_id))
    await clb.answer('Админ был успешно удален')
    await dialog_manager.switch_to(adminSG.admin_menu)


async def admin_del_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admins = await session.get_admins()
    buttons = []
    for admin in admins:
        buttons.append((admin.name, admin.user_id))
    return {'items': buttons}


async def refresh_url(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    id: str = dialog_manager.dialog_data.get('link_id')
    dialog_manager.dialog_data.clear()
    await session.del_link(id)
    await dialog_manager.switch_to(adminSG.admin_add)


async def admin_add_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    id = get_random_id()
    dialog_manager.dialog_data['link_id'] = id
    await session.add_link(id)
    return {'id': id}


async def admin_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admins = await session.get_admins()
    text = ''
    for admin in admins:
        text += f'{admin.name}\n'
    return {'admins': text}


async def get_mail(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    if msg.text:
        dialog_manager.dialog_data['text'] = msg.text
    elif msg.photo:
        dialog_manager.dialog_data['photo'] = msg.photo[0].file_id
        dialog_manager.dialog_data['caption'] = msg.caption
    elif msg.video:
        dialog_manager.dialog_data['video'] = msg.video.file_id
        dialog_manager.dialog_data['caption'] = msg.caption
    else:
        await msg.answer('Что-то пошло не так, пожалуйста попробуйте снова')
    await dialog_manager.switch_to(adminSG.get_time)


async def get_time(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        time = datetime.datetime.strptime(text, '%H:%M %d.%m')
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['time'] = text
    await dialog_manager.switch_to(adminSG.get_keyboard)


async def get_mail_keyboard(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        buttons = text.split('\n')
        keyboard: list[tuple] = [(i.split('-')[0].strip(), i.split('-')[1].strip()) for i in buttons]
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['keyboard'] = keyboard
    await dialog_manager.switch_to(adminSG.confirm_mail)


async def cancel_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def start_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    time = dialog_manager.dialog_data.get('time')
    keyboard = dialog_manager.dialog_data.get('keyboard')
    if keyboard:
        keyboard = [InlineKeyboardButton(text=i[0], url=i[1]) for i in keyboard]
    users = await session.get_users()
    if not time:
        if dialog_manager.dialog_data.get('text'):
            text: str = dialog_manager.dialog_data.get('text')
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.user_id,
                        text=text.format(name=user.name),
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                    )
                    if user.active == 0:
                        await session.set_active(user.user_id, 1)
                except Exception as err:
                    print(err)
                    await session.set_active(user.user_id, 0)
        elif dialog_manager.dialog_data.get('caption'):
            caption: str = dialog_manager.dialog_data.get('caption')
            if dialog_manager.dialog_data.get('photo'):
                for user in users:
                    try:
                        await bot.send_photo(
                            chat_id=user.user_id,
                            photo=dialog_manager.dialog_data.get('photo'),
                            caption=caption.format(name=user.name),
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                        )
                        if user.active == 0:
                            await session.set_active(user.user_id, 1)
                    except Exception as err:
                        print(err)
                        await session.set_active(user.user_id, 0)
            else:
                for user in users:
                    try:
                        await bot.send_video(
                            chat_id=user.user_id,
                            video=dialog_manager.dialog_data.get('video'),
                            caption=caption.format(name=user.name),
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                        )
                        if user.active == 0:
                            await session.set_active(user.user_id, 1)
                    except Exception as err:
                        print(err)
                        await session.set_active(user.user_id, 0)
    else:
        date = datetime.datetime.strptime(time, '%H:%M %d.%m')
        date = date.replace(year=datetime.datetime.today().year)
        scheduler.add_job(
            func=send_messages,
            args=[bot, session, InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None],
            kwargs={
                'text': dialog_manager.dialog_data.get('text'),
                'caption': dialog_manager.dialog_data.get('caption'),
                'photo': dialog_manager.dialog_data.get('photo'),
                'video': dialog_manager.dialog_data.get('video')
            },
            next_run_time=date
        )
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def prices_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    relation = await session.get_rate_price('relation')
    old = await session.get_rate_price('old')
    future = await session.get_rate_price('future')
    question = await session.get_rate_price('question')

    text = (f'"Диагностика отношений": {relation}₽\n'
            f'"Вернется ли бывший": {old}₽\n'
            f'"Будущее на 3 месяца": {future}₽\n'
            f'"Стоимость допродажи": {question}₽\n')
    return {
        'text': text
    }


async def change_price_choose(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    rate = clb.data.split('_')[0]
    await dialog_manager.switch_to(adminSG.get_price)


async def get_price(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        price = int(text)
    except Exception:
        await msg.answer('Новая цена должна быть числом, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate = dialog_manager.dialog_data.get('rate')
    await session.set_rate_price(rate, price)
    await dialog_manager.switch_to(adminSG.prices)


async def get_button_name(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['name'] = text
    await dialog_manager.switch_to(adminSG.get_button_link)


async def save_without_name(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    bot: Bot = dialog_manager.middleware_data.get('bot')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    chat = await bot.get_chat(chat_id)
    dialog_manager.dialog_data['name'] = chat.title
    await dialog_manager.switch_to(adminSG.get_button_link)


async def save_without_link(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    bot: Bot = dialog_manager.middleware_data.get('bot')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    name = dialog_manager.dialog_data.get('name')
    chat = await bot.get_chat(chat_id)
    await session.add_op(
        chat_id=chat_id,
        name=name,
        link=chat.invite_link,
    )
    await clb.answer('Кнопка на ОП была успешно сохранена')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def get_button_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if len(text.split('/')) <= 1:
        await msg.answer('Вы ввели ссылку не в том формате, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    name = dialog_manager.dialog_data.get('name')
    await session.add_op(
        chat_id=chat_id,
        name=name,
        link=text,
    )
    await msg.answer('Кнопка на ОП была успешно сохранена')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def op_buttons_switcher(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['chat_id'] = int(item_id)
    await dialog_manager.switch_to(adminSG.button_menu)


async def button_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    button = await session.get_op_by_chat_id(chat_id)
    return {
        'join': button.entry,
        'channel_name': button.name,
        'channel_link': button.link
    }


async def del_op_channel(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    await session.del_op_channel(chat_id)
    await clb.answer('Канал был успешно удален с ОП')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.op_menu)


async def change_button_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    await session.set_button_link(chat_id, link=text)
    await dialog_manager.switch_to(adminSG.button_menu)


async def op_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    categories = await session.get_op()
    text = ''
    buttons = []
    count = 1
    for category in categories:
        buttons.append((category.name, category.chat_id))
        text += f'{count}: {category.name} - {category.link} | {category.entry} вхождений\n'
        count += 1
    return {
        'buttons': text,
        'items': buttons
    }


async def get_op_channel(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    await msg.delete()
    try:
        chat_id = int(text)
    except Exception:
        fragments = text.split('/')
        if len(fragments) <= 1:
            await msg.answer('Отправленное вами сообщение не воспринимается ссылок, пожалуйста попробуйте еще раз')
            return
        chat_id = '@' + fragments[-1]
    try:
        chat = await msg.bot.get_chat(chat_id)
    except Exception:
        await msg.answer('К сожалению такого канала не найдено или вы не добавили бота в канал | чат c '
                         'админскими правами, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    op_channels = await session.get_op()
    if chat.id in [channel.chat_id for channel in op_channels]:
        await msg.answer('Этот канал уже добавлен на ОП, чтобы добавить его повторно удалите его')
        return
    dialog_manager.dialog_data['chat_id'] = chat.id
    await dialog_manager.switch_to(adminSG.get_button_name)
