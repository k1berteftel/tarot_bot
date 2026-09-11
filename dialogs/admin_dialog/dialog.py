from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Cancel
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.admin_dialog import getters
from states.state_groups import adminSG


admin_dialog = Dialog(
    Window(
        Const('Админ панель'),
        Column(
            Button(Const('📊 Получить статистику'), id='get_static', on_click=getters.get_static),
            SwitchTo(Const('🛫Сделать рассылку'), id='mailing_menu_switcher', state=adminSG.get_mail),
            SwitchTo(Const('Управление ценами'), id='prices_switcher', state=adminSG.prices),
            SwitchTo(Const('🔗 Управление диплинками'), id='deeplinks_menu_switcher', state=adminSG.deeplinks_menu),
            SwitchTo(Const('👥 Управление админами'), id='admin_menu_switcher', state=adminSG.admin_menu),
            SwitchTo(Const('Управление ОП'), id='op_menu_switcher', state=adminSG.op_menu),
            Button(Const('📋Выгрузка базы пользователей'), id='get_users_txt', on_click=getters.get_users_txt),
        ),
        Cancel(Const('Назад'), id='close_admin'),
        state=adminSG.start
    ),
    Window(
        Format('{text}'),
        Const('Для изменения цены выберите название тарифа, цену которого вы хотели бы изменить'),
        Column(
            Button(Const('Диагностика отношений'), id='relation_price_change', on_click=getters.change_price_choose),
            Button(Const('Вернется ли бывший'), id='old_price_change', on_click=getters.change_price_choose),
            Button(Const('Будущее на 3 месяца'), id='future_price_change', on_click=getters.change_price_choose),
            Button(Const('Вопросы допродажи'), id='question_price_change', on_click=getters.change_price_choose),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.prices_getter,
        state=adminSG.prices
    ),
    Window(
        Const('Введите новую цену за тариф'),
        TextInput(
            id='get_price',
            on_success=getters.get_price
        ),
        SwitchTo(Const('🔙 Назад'), id='back_prices', state=adminSG.prices),
        state=adminSG.get_price
    ),
    Window(
        Format('🔗 *Меню управления диплинками*'),
        Column(
            Select(
                Format('{item[0]}'),
                id='deeplinks_menu_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.deeplink_choose
            ),
        ),
        Row(
            Button(Const('◀️'), id='back_deeplinks_pager', on_click=getters.deeplinks_pager, when='not_first'),
            Button(Format('{page}'), id='deeplinks_pager', when='deeplinks'),
            Button(Const('▶️'), id='next_deeplinks_pager', on_click=getters.deeplinks_pager, when='not_last')
        ),
        SwitchTo(Const('➕ Добавить диплинк'), id='add_deeplink', state=adminSG.get_deeplink_name),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.deeplinks_menu_getter,
        state=adminSG.deeplinks_menu
    ),
    Window(
        Const('Введите название для данной ссылки'),
        TextInput(
            id='get_link_name',
            on_success=getters.get_deeplink_name
        ),
        SwitchTo(Const('🔙 Назад'), id='back_deeplinks_menu', state=adminSG.deeplink_menu),
        state=adminSG.get_deeplink_name
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Const('🗑Удалить диплинк'), id='del_deeplink', on_click=getters.del_deeplink),
        ),
        SwitchTo(Const('🔙 Назад'), id='back_deeplinks_menu', state=adminSG.deeplinks_menu),
        getter=getters.deeplink_menu_getter,
        state=adminSG.deeplink_menu
    ),
    Window(
        Format('👥 *Меню управления администраторами*\n\n {admins}'),
        Column(
            SwitchTo(Const('➕ Добавить админа'), id='add_admin_switcher', state=adminSG.admin_add),
            SwitchTo(Const('❌ Удалить админа'), id='del_admin_switcher', state=adminSG.admin_del)
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.admin_menu_getter,
        state=adminSG.admin_menu
    ),
    Window(
        Const('👤 Выберите пользователя, которого хотите сделать админом\n'
              '⚠️ Ссылка одноразовая и предназначена для добавления только одного админа'),
        Column(
            Url(Const('🔗 Добавить админа (ссылка)'), id='add_admin',
                url=Format('http://t.me/share/url?url=https://t.me/VedmaAstroBot?start={id}')),  # поменять ссылку
            Button(Const('🔄 Создать новую ссылку'), id='new_link_create', on_click=getters.refresh_url),
            SwitchTo(Const('🔙 Назад'), id='back_admin_menu', state=adminSG.admin_menu)
        ),
        getter=getters.admin_add_getter,
        state=adminSG.admin_add
    ),
    Window(
        Const('❌ Выберите админа для удаления'),
        Group(
            Select(
                Format('👤 {item[0]}'),
                id='admin_del_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_admin
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back_admin_menu', state=adminSG.admin_menu),
        getter=getters.admin_del_getter,
        state=adminSG.admin_del
    ),
    Window(
        Const('Введите сообщение которое вы хотели бы разослать\n\n<b>Предлагаемый макросы</b>:'
              '\n{name} - <em>полное имя пользователя</em>'),
        MessageInput(
            content_types=ContentType.ANY,
            func=getters.get_mail
        ),
        SwitchTo(Const('Назад'), id='back', state=adminSG.start),
        state=adminSG.get_mail
    ),
    Window(
        Const('Введите дату и время в которое сообщение должно отправиться всем юзерам в формате '
              'час:минута:день:месяц\n Например: 18:00 10.02 (18:00 10-ое февраля)'),
        TextInput(
            id='get_time',
            on_success=getters.get_time
        ),
        SwitchTo(Const('Продолжить без отложки'), id='get_keyboard_switcher', state=adminSG.get_keyboard),
        SwitchTo(Const('Назад'), id='back_get_mail', state=adminSG.get_mail),
        state=adminSG.get_time
    ),
    Window(
        Const('Введите кнопки которые будут крепиться к рассылаемому сообщению\n'
              'Введите кнопки в формате:\n кнопка1 - ссылка1\nкнопка2 - ссылка2'),
        TextInput(
            id='get_mail_keyboard',
            on_success=getters.get_mail_keyboard
        ),
        SwitchTo(Const('Продолжить без кнопок'), id='confirm_mail_switcher', state=adminSG.confirm_mail),
        SwitchTo(Const('Назад'), id='back_get_time', state=adminSG.get_time),
        state=adminSG.get_keyboard
    ),
    Window(
        Const('Вы подтверждаете рассылку сообщения'),
        Row(
            Button(Const('Да'), id='start_malling', on_click=getters.start_malling),
            Button(Const('Нет'), id='cancel_malling', on_click=getters.cancel_malling),
        ),
        SwitchTo(Const('Назад'), id='back_get_keyboard', state=adminSG.get_keyboard),
        state=adminSG.confirm_mail
    ),
    Window(
        Format('📋 *Меню управления ОП*\n\n'
               '📋 *Действующие каналы*:\n\n {buttons}'),
        Column(
            SwitchTo(Const('➕ Добавить канал'), id='get_op_channel_switcher', state=adminSG.get_op_channel),
        ),
        Group(
            Select(
                Format('💼 {item[0]}'),
                id='buttons_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.op_buttons_switcher
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.op_menu_getter,
        state=adminSG.op_menu
    ),
    Window(
        Const("Отправьте ссылку канал (если он открытый) или его chat ID если канал закрытый\n\n"
              "<b>❗️Перед этим добавьте бота в канал и назначьте админом, со всеми правами</b>"),
        TextInput(
            id='get_op_chat_id',
            on_success=getters.get_op_channel
        ),
        SwitchTo(Const('Назад'), id='back_op_menu', state=adminSG.op_menu),
        state=adminSG.get_op_channel
    ),
    Window(
        Const('Введите название для кнопки канал или нажмите пропустить, чтобы бот сам подобрал название для канала'),
        TextInput(
            id='get_button_name',
            on_success=getters.get_button_name
        ),
        Button(Const('⏭ Пропустить'), id='continue_no_name', on_click=getters.save_without_name),
        state=adminSG.get_button_name
    ),
    Window(
        Const('🔗 Введите свою ссылку на канал или пропустите этот шаг, '
              'чтобы бот сам подобрал ссылку для канала или чата'),
        TextInput(
            id='get_button_link',
            on_success=getters.get_button_link
        ),
        Button(Const('⏭ Пропустить'), id='continue_no_link', on_click=getters.save_without_link),
        state=adminSG.get_button_link
    ),
    Window(
        Format('Канал|Чат {channel_name}\nУказанная ссылка на канал|чат: {channel_link}\nВхождений: {join}'),
        Column(
            SwitchTo(Const('Изменить ссылку на канал'), id='change_button_link_switcher',
                     state=adminSG.change_button_link),
            Button(Const('➖Удалить канал с ОП'), id='del_op_channel', on_click=getters.del_op_channel),
        ),
        SwitchTo(Const('Назад'), id='back_op_menu', state=adminSG.op_menu),
        getter=getters.button_menu_getter,
        state=adminSG.button_menu
    ),
    Window(
        Const('🔗 Введите новую ссылку для кнопки\n\n'
              '⚠️ <em>Важно: ссылка должна вести на тот же канал, иначе могут возникнуть проблемы с проверкой ОП</em>'),
        TextInput(
            id='change_button_link',
            on_success=getters.change_button_link
        ),
        state=adminSG.change_button_link
    ),
)