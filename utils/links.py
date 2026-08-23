from urllib.parse import quote
from aiogram.utils.link import create_telegram_link


def get_user_text_link(username: str, text: str):
    encoded_text = quote(text)

    return create_telegram_link(username, text=encoded_text)