from urllib.parse import quote
from aiogram.utils.link import create_telegram_link


def get_user_text_link(username: str, text: str):
    base_link = create_telegram_link(username)
    # Кодируем текст так, чтобы пробелы были %20
    encoded_text = quote(text, safe='')
    return f"{base_link}?text={encoded_text}"
