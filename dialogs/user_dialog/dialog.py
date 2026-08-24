from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.user_dialog import getters
from utils.links import get_user_text_link

from states.state_groups import startSG, adminSG

user_dialog = Dialog(
    Window(
        DynamicMedia('media'),
        Const('Добро пожаловать 🌙\n\nЯ твоя личная ведьма-таролог 🔮\nПомогу разобраться в ситуации с помощью карт '
              'Таро — посмотрим чувства, отношения, деньги и то, что пока остаётся скрытым ✨\n\n'
              '<b>🎁 Бесплатный расклад — 1 раз в день!</b>\n\nТакже могу провести ритуал, вернуть бывшего '
              'или сделать привязку к нынешнему партнёру ❤️'),
        Column(
            Button(Const('❤️ Диагностика отношений'), id='relation_rate_choose', on_click=getters.choose_rate),
            Button(Const('💔 Вернется ли бывший'), id='old_rate_choose', on_click=getters.choose_rate),
            Button(Const('🎴 Одна карта'), id='one_card_choose', on_click=getters.one_card),
            #Button(Const('💰 Финансы и работа'), id='finance_rate_choose', on_click=getters.choose_rate),
            # TODO:
            Button(Const('✨ Будущее на 3 месяца'), id='future_rate_choose', on_click=getters.choose_rate),
            Url(Const('🕯Ритуал'), id='ritual_url', url=Const(get_user_text_link(
                username=f'vedymasay',
                text='Какой-то текст'
            ))),
            #Button(Const('🔮 Вопрос-ответ'), id='question_rate_choose', on_click=getters.choose_rate),
            Start(Const('Админ панель'), id='admin', state=adminSG.start, when='admin')
        ),
        getter=getters.start_getter,
        state=startSG.start
    )
)