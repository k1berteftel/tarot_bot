from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Back, Cancel
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.form_dialog import getters

from states.state_groups import FormSG


form_dialog = Dialog(
    Window(
        Const('<tg-emoji emoji-id="5765009678002033928">✍</tg-emoji>Введите ваше имя:'),
        TextInput(
            id='get_name',
            on_success=getters.get_name
        ),
        Cancel(Const('🏘В главное меню'), id='close_dialog'),
        state=FormSG.get_name,
    ),
    Window(
        Const('<tg-emoji emoji-id="5765009678002033928">✍</tg-emoji>Введите вашу дату рождения <em>(в формате дд.мм.гггг)</em>:'),
        TextInput(
            id='get_birthday',
            on_success=getters.get_birthday
        ),
        state=FormSG.get_birthday
    ),
    Window(
        Const('<tg-emoji emoji-id="5765009678002033928">✍</tg-emoji>Введите имя партнера:'),
        TextInput(
            id='get_partner_name',
            on_success=getters.get_partner_name
        ),
        Back(Const('Назад'), id='back', style=Style(emoji_id="5388584622328131561")),
        state=FormSG.get_partner_name
    ),
    Window(
        Const('<tg-emoji emoji-id="5765009678002033928">✍</tg-emoji>Введите дату рождения партнера (в формате дд.мм.гггг):'),
        TextInput(
            id='get_partner_birthday',
            on_success=getters.get_partner_birthday
        ),
        Back(Const('Назад'), id='back', style=Style(emoji_id="5388584622328131561")),
        state=FormSG.get_partner_birthday
    ),
    Window(
        Const('<tg-emoji emoji-id="5765009678002033928">✍</tg-emoji>Опишите вашу ситуацию подробно:'),
        Format('Например:\n<blockquote>{example}</blockquote>'),
        TextInput(
            id='get_situation',
            on_success=getters.get_situation
        ),
        Button(Const('Назад'), id='back', on_click=getters.back_situation, style=Style(emoji_id="5388584622328131561")),
        getter=getters.get_situation_getter,
        state=FormSG.get_situation
    ),
    Window(
        Const('<tg-emoji emoji-id="5765009678002033928">✍</tg-emoji>Введите ваш текущий род деятельности:'),
        TextInput(
            id='get_activity',
            on_success=getters.get_activity
        ),
        SwitchTo(Const('Назад'), id='back', state=FormSG.get_birthday, style=Style(emoji_id="5388584622328131561")),
        state=FormSG.get_activity
    ),
    Window(
        Const('<tg-emoji emoji-id="5765009678002033928">✍</tg-emoji>Выберите или введите вручную ваш финансовый запрос:'),
        TextInput(
            id='get_request',
            on_success=getters.get_request
        ),
        Group(
            Select(
                Format('{item[0]}'),
                id='choose_request_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.request_selector
            ),
            width=1
        ),
        Back(Const('Назад'), id='back', style=Style(emoji_id="5388584622328131561")),
        getter=getters.get_request_getter,
        state=FormSG.get_request
    ),
    Window(
        Const('👨‍🏫Какая сфера жизни вас интересует'),
        Group(
            Select(
                Format('{item[0]}'),
                id='choose_sphere_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.sphere_selector
            ),
            width=1
        ),
        SwitchTo(Const('Назад'), id='back', state=FormSG.get_birthday, style=Style(emoji_id="5388584622328131561")),
        getter=getters.choose_sphere_getter,
        state=FormSG.get_sphere
    ),    Window(
        Const('<tg-emoji emoji-id="5436113877181941026">❓</tg-emoji>Есть ли у вас конкретный вопрос или цель на ближайшие 3 месяца?'),
        TextInput(
            id='get_purpose',
            on_success=getters.get_purpose
        ),
        Back(Const('Назад'), id='back', style=Style(emoji_id="5388584622328131561")),
        state=FormSG.get_purpose
    ),
    # Окно вопрос-ответ
    Window(
        Const('<tg-emoji emoji-id="5765009678002033928">✍</tg-emoji>Введите интересующий вас вопрос:'),
        TextInput(
            id='get_question',
            on_success=getters.get_question
        ),
        state=FormSG.get_question
    ),

    Window(
        Format('{text}'),
        Column(
            Button(Const('Перейти к оплате'), id='payment_dialog_switcher', on_click=getters.payment_dialog_switcher, style=Style(emoji_id="5801180866071760635")),
        ),
        getter=getters.fee_getter,
        state=FormSG.fee
    ),
)