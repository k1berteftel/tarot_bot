from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode

from keyboards.upsell import get_upsell_keyboard
from database.action_data_class import DataInteraction
from states.state_groups import startSG, PaymentSG


user_router = Router()


@user_router.message(CommandStart())
async def start_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, command: CommandObject):
    args = command.args
    #referral = None
    if args:
        link_ids = await session.get_links()
        ids = [i.link for i in link_ids]
        if args in ids:
            await session.add_admin(msg.from_user.id, msg.from_user.full_name)
            await session.del_link(args)
        if not await session.check_user(msg.from_user.id):
            deeplinks = await session.get_deeplinks()
            deep_list = [i.link for i in deeplinks]
            if args in deep_list:
                await session.add_entry(args)
            #try:
                #args = int(args)
                #users = [user.user_id for user in await session.get_users()]
                #if args in users:
                    #referral = args
                    #await session.add_refs(args)
            #except Exception as err:
                #print(err)
    await session.add_user(msg.from_user.id, msg.from_user.username if msg.from_user.username else 'Отсутствует',
                           msg.from_user.full_name)
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
    await dialog_manager.start(state=startSG.start, mode=StartMode.RESET_STACK)


@user_router.callback_query(F.data.startswith('question_'))
async def handle_choose_upsell_question(clb: CallbackQuery, dialog_manager: DialogManager, session: DataInteraction, state: FSMContext):
    data = await state.get_data()
    questions = data.get('questions', [])
    await clb.answer()
    try:
        await clb.message.delete()
    except Exception:
        ...
    if not questions:
        await clb.message.answer('Во время обработки вопроса произошла неизвестная ошибка, '
                                 'пожалуйста обратитесь в поддержку или вернитесь в главное меню /start')
        return
    question_id = clb.data.split('_')[-1]
    cost = await session.get_rate_price('question')
    question = questions[int(question_id)]
    await state.update_data(target_question=question, cost=cost)
    text = f"""🔮 Я принял ваш вопрос:
<i>«{question}»</i>

Сейчас я проведу дополнительный расклад, который даст ответ именно на этот вопрос. 
Карты уже ждут вашего запроса.

<b>🃏 О стоимости:</b>
Стоимость этого расклада составляет {cost} рублей.

<b>💡 Как проходит сеанс:</b>
После подтверждения оплаты я погружаюсь в ваш вопрос, вытягиваю карты и формулирую послание специально для вас. На это уходит <b>от 2 до 4 минут</b>.

👉 Чтобы получить ответ на ваш вопрос, нажмите кнопку <b>«Перейти к оплате»</b>.

<em>После успешной оплаты вы получите уведомление о начале сеанса, а через пару минут — готовый расклад прямо в этот чат.</em>
"""
    keyboard = await get_upsell_keyboard()
    await clb.message.answer(
        text=text,
        reply_markup=keyboard
    )


@user_router.callback_query(F.data.startswith('upsell_payment'))
async def handle_payment_switcher(clb: CallbackQuery, dialog_manager: DialogManager, session: DataInteraction, state: FSMContext):
    data = await state.get_data()
    ai_context = data.get('ai_context')
    data: dict = data.get('ai_data')
    question = data.get('target_question')
    cost = data.get('cost')

    data['question'] = question
    data['ai_context'] = ai_context
    data['cost'] = cost
    await clb.message.delete()
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await clb.bot.delete_message(chat_id=clb.from_user.id, message_id=clb.message.message_id - 1)
        except Exception:
            ...
    await state.clear()
    await dialog_manager.start(PaymentSG.menu, data=data)


