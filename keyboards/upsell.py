from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_upsell_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к оплате', callback_data='upsell_payment_switcher')]
    ])
    return keyboard