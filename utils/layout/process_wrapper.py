import asyncio
import random
import logging
from typing import Optional, Callable, Awaitable

from aiogram import Bot
from aiogram.types import Message

logger = logging.getLogger(__name__)

# ============================================
# Тексты для разных этапов
# ============================================

STAGES = {
    'init': {
        'texts': [
            '🔮 Принимаю ваш запрос... Карты чувствуют ваш интерес',
            '📜 Открываю ваш вопрос перед Арканами...',
            '🕯 Зажигаю свечи для вашего расклада...',
            '🌟 Настраиваюсь на вашу энергию...',
            '🌀 Карты начинают движение в вашу сторону...'
        ]
    },
    'analysis': {
        'texts': [
            '⚡️ Считываю энергетику вашего вопроса...',
            '🌙 Раскладываю карты по лунным фазам...',
            '💫 Соединяю вашу ситуацию с символами Арканов...',
            '🔥 Карты нагреваются вашим вопросом...',
            '🌊 Поток энергии направляется к картам...'
        ]
    },
    'visualization': {
        'texts': [
            '🃏 Карты ложатся на стол... Первая карта готова',
            '🎴 Вторая карта раскрывает свои символы...',
            '📿 Третья карта выходит из тени...',
            '🗡 Арканы занимают свои позиции...',
            '🌌 Карты выстраиваются в ваш узор судьбы...'
        ]
    },
    'interpretation': {
        'texts': [
            '🧠 Читаю послания каждой карты...',
            '📖 Расшифровываю символы Арканов...',
            '🔍 Нахожу скрытые смыслы в вашем раскладе...',
            '💭 Связываю карты в единую историю...',
            '✨ Интерпретирую ваш путь по картам...'
        ]
    },
    'assembly': {
        'texts': [
            '📝 Составляю послание для вас...',
            '🎁 Формирую ответ Арканов...',
            '💎 Карты шепчут свой ответ...',
            '📨 Упаковываю мудрость в сообщение...',
            '🌟 Финальная обработка вашего расклада...'
        ]
    },
    'final': {
        'texts': [
            '🎆 Расклад готов! Сейчас всё пришлю...',
            '🌟 Карты заговорили! Получайте ответ...',
            '💫 Ваше будущее уже близко...'
        ]
    }
}


def get_random_text(stage_key: str) -> str:
    """Возвращает случайный текст для этапа"""
    stage = STAGES.get(stage_key, STAGES['init'])
    return random.choice(stage['texts'])


def get_stage_key(percent: int) -> str:
    """Определяет этап по проценту"""
    if percent < 15:
        return 'init'
    elif percent < 35:
        return 'analysis'
    elif percent < 55:
        return 'visualization'
    elif percent < 80:
        return 'interpretation'
    elif percent < 95:
        return 'assembly'
    else:
        return 'final'


def _progress_bar(percent: int, length: int = 12) -> str:
    """Создает полоску прогресса"""
    filled = int((percent / 100) * length)
    empty = length - filled

    if percent < 30:
        fill_char = '🟣'
    elif percent < 60:
        fill_char = '🟡'
    elif percent < 90:
        fill_char = '🟠'
    else:
        fill_char = '✨'

    if percent < 100:
        sparkles = ['✦', '·', '✧', '•']
        empty_part = ''.join(random.choice(sparkles) if random.random() > 0.7 else '⬜'
                             for _ in range(empty))
        return f"{fill_char * filled}{empty_part} {percent}%"
    else:
        return f"🌟 {'⭐' * length} 100%"


def _progress_text(percent: int) -> str:
    """Генерирует текст с прогрессом"""
    stage_key = get_stage_key(percent)
    text = get_random_text(stage_key)
    dots = '.' * (percent % 3 + 1)

    return f"{text}{dots}\n\n{_progress_bar(percent)}"


# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАДЕРЖКИ
# ============================================

async def wait_with_progress(
        user_id: int,
        bot: Bot,
        min_seconds: int = 120,
        max_seconds: int = 300
) -> Message:
    """
    Имитация процесса с ползунком прогресса

    Args:
        user_id: Грубо говоря ID чата, где мы будем редактировать сообщение
        bot: Объект бота
        min_seconds: Минимальная длительность (секунд)
        max_seconds: Максимальная длительность (секунд)

    Пример:
        msg = await bot.send_message(chat_id, "⏳ Начинаю расклад...")
        await wait_with_progress(msg)  # Ждем 2-5 минут
        await msg.delete()
        # Дальше отправляем результат
    """
    # Выбираем случайную длительность
    duration = random.randint(min_seconds, max_seconds)
    logger.info(f"⏱ Имитация процесса: {duration} секунд")

    # Этапы с разной скоростью
    stages = [
        {'percent': 15, 'weight': 0.15},
        {'percent': 35, 'weight': 0.20},
        {'percent': 55, 'weight': 0.25},
        {'percent': 80, 'weight': 0.20},
        {'percent': 95, 'weight': 0.10},
        {'percent': 100, 'weight': 0.10},
    ]

    current_percent = 0

    message = await bot.send_message(
        chat_id=user_id,
        text=_progress_text(int(current_percent))
    )

    for stage in stages:
        target_percent = stage['percent']
        weight = stage['weight']

        # Время на этот этап
        stage_duration = duration * weight

        # Разбиваем на шаги
        steps = random.randint(5, 10)
        step_percent = (target_percent - current_percent) / steps
        step_delay = stage_duration / steps

        for _ in range(steps):
            current_percent += step_percent
            current_percent = min(current_percent, target_percent)

            text = _progress_text(int(current_percent))

            try:
                await message.edit_text(text)
            except Exception as e:
                logger.warning(f"Не удалось обновить сообщение: {e}")

            await asyncio.sleep(step_delay * random.uniform(0.8, 1.2))

        current_percent = target_percent

    # Финальное сообщение
    try:
        await message.edit_text(_progress_text(100))
    except Exception as e:
        logger.warning(f"Не удалось обновить сообщение: {e}")
    return message


