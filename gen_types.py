from typing import Literal
from pydantic import BaseModel

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class BaseAiMessage(BaseModel):
    role: Literal['assistant', 'user']
    content: str


class CardMessage(BaseModel):
    text: str
    image: str  # путь до изображения


class PackedMultiMessage(BaseModel):
    text: str
    card_messages: list[CardMessage]
    messages: list[BaseAiMessage] = []


class UpSellMessage(BaseModel):
    text: str
    keyboard: InlineKeyboardMarkup
    questions: list[str]