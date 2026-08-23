from aiogram.fsm.state import State, StatesGroup

# Обычная группа состояний


class startSG(StatesGroup):
    start = State()


class FormSG(StatesGroup):
    get_name = State()
    get_birthday = State()
    get_situation = State()

    get_partner_name = State()
    get_partner_birthday = State()

    get_activity = State()
    get_request = State()

    get_sphere = State()
    get_purpose = State()

    get_question = State()

    fee = State()


class PaymentSG(StatesGroup):
    menu = State()
    process_payment = State()


class SubSG(StatesGroup):
    start = State()


class adminSG(StatesGroup):
    start = State()

    get_mail = State()
    get_time = State()
    get_keyboard = State()
    confirm_mail = State()

    deeplink_menu = State()
    deeplink_del = State()

    admin_menu = State()
    admin_del = State()
    admin_add = State()

    op_menu = State()
    get_op_channel = State()
    get_button_name = State()
    get_button_link = State()
    button_menu = State()
    change_button_text = State()
    change_button_link = State()

    prices = State()
    get_price = State()
