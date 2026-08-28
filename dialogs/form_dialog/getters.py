import asyncio
from datetime import datetime

from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from utils.layout.arranging import process_arranging
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import startSG, FormSG, PaymentSG


request_buttons = [
    ('Увеличить доход', 'earn'),
    ('Сменить работу', 'job'),
    ('Боюсь увольнения', 'dismissal'),
    ('Открыть бизнеc', 'business'),
    ('Общий прогноз', 'forecast')
]


sphere_buttons = [
    ('Личная жизнь', 'life'),
    ('Карьера и деньги', 'career'),
    ('Здоровье', 'health'),
    ('Все сферы сразу', 'all')
]


async def get_name(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data.clear()
    if dialog_manager.start_data:
        dialog_manager.dialog_data.update(dialog_manager.start_data)
        dialog_manager.start_data.clear()
    dialog_manager.dialog_data['name'] = text
    await dialog_manager.switch_to(FormSG.get_birthday)


async def get_birthday(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        birthday = datetime.strptime(text.strip(), "%d.%m.%Y")
    except Exception as err:
        print(err)
        await msg.answer('❗️Дата рождения не соответствует формату указанному выше, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['birthday'] = birthday
    rate = dialog_manager.dialog_data.get('rate')
    if rate in ['relation', 'old']:
        await dialog_manager.switch_to(FormSG.get_partner_name)
    if rate == 'finance':
        await dialog_manager.switch_to(FormSG.get_request)
    if rate == 'future':
        await dialog_manager.switch_to(FormSG.get_sphere)


async def get_partner_name(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['partner_name'] = text
    await dialog_manager.switch_to(FormSG.get_partner_birthday)


async def get_partner_birthday(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        birthday = datetime.strptime(text, "%d.%m.%Y")
    except Exception:
        await msg.answer('❗️Дата рождения не соответствует формату указанному выше, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['partner_birthday'] = birthday
    await dialog_manager.switch_to(FormSG.get_situation)


async def get_situation_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    rate = dialog_manager.dialog_data.get('rate')
    examples = {
        'relation': 'Мы встречаемся 8 месяцев. В последние 2 недели партнёр стал холодным, реже пишет, отменяет встречи. Я чувствую тревогу и не понимаю, в чём причина',
        'old': 'Расстались 2 месяца назад по инициативе партнёра. Причина — я не уделял(а) достаточно внимания. Сейчас мы изредка переписываемся. Я хочу понять, есть ли у него(неё) желание вернуться',
        'finance': 'Работаю 2 года. Зарплата не растёт. Хочу понять, стоит ли рисковать и куда двигаться'
    }
    return {
        'example': examples.get(rate)
    }


async def get_situation(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['situation'] = text
    #await dialog_manager.switch_to(FormSG.fee)
    state: FSMContext = dialog_manager.middleware_data.get('state')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    task = asyncio.create_task(process_arranging(
        dialog_manager.dialog_data,
        msg.from_user.id,
        bot,
        state
    ))
    # pass  # TODO: перевод на форму оплаты с продающим текстом для 3 типов раскладов


async def back_situation(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    rate = dialog_manager.dialog_data.get('rate')
    if rate in ['relation', 'old']:
        await dialog_manager.switch_to(FormSG.get_partner_birthday)
    else:
        await dialog_manager.switch_to(FormSG.get_request)


async def get_activity(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['activity'] = text
    await dialog_manager.switch_to(FormSG.get_request)


async def get_request_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    return {
        'items': request_buttons
    }


async def get_request(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['request'] = text
    await dialog_manager.switch_to(FormSG.get_situation)


async def request_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    request = None
    for request_btn in request_buttons:
        if request_btn[1] == item_id:
            request = request_btn[0]
            break
    dialog_manager.dialog_data['request'] = request
    await dialog_manager.switch_to(FormSG.get_situation)


async def choose_sphere_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    return {
        'items': sphere_buttons
    }


async def sphere_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    sphere = None
    for sphere_btn in sphere_buttons:
        if sphere_btn[1] == item_id:
            sphere = sphere_btn[0]
    dialog_manager.dialog_data['sphere'] = sphere
    await dialog_manager.switch_to(FormSG.get_purpose)


async def get_purpose(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['purpose'] = text
    state: FSMContext = dialog_manager.middleware_data.get('state')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    task = asyncio.create_task(process_arranging(
        dialog_manager.dialog_data,
        msg.from_user.id,
        bot,
        state
    ))
    #await dialog_manager.switch_to(FormSG.fee)


async def get_question(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    pass  # TODO генерация кастомных вопросов от ИИ


async def fee_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate = dialog_manager.dialog_data.get('rate')
    cost = await session.get_rate_price(rate)
    if not dialog_manager.start_data:
        text = (f'📋 Ваш запрос принят. Благодарим за доверие! 🔮\n\n<b>🃏 Стоимость расклада — {cost} ₽</b>\n\n'
                f'После оплаты начнётся разбор вашего запроса. В течение нескольких минут вы получите подробную '
                f'интерпретацию карт и ответ прямо в этом чате ✨\n\n👉 Нажмите <b>«Перейти к оплате»</b>, '
                f'чтобы продолжить.\n<blockquote>После успешной оплаты вы получите уведомление о начале сеанса, '
                f'а через пару минут — готовый текст с расшифровкой прямо в этот чат.</blockquote>')
    else:
        text = dialog_manager.start_data.get('text')
    return {
        'text': text
    }


async def payment_dialog_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate = dialog_manager.dialog_data.get('rate')
    cost = await session.get_rate_price(rate)
    data = dialog_manager.dialog_data
    data.update(cost=cost)
    await dialog_manager.start(PaymentSG.menu, data=data)

