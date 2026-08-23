import json
import logging
import os
import tempfile
from typing import Optional, List, Dict, Any
from datetime import datetime
from PIL import Image

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from gen_types import CardMessage, PackedMultiMessage, UpSellMessage

logger = logging.getLogger(__name__)


# ============================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ СОХРАНЕНИЯ ИЗОБРАЖЕНИЙ
# ============================================

def save_image_to_temp(image: Image.Image, card_name: str = "card") -> str:
    """
    Сохраняет PIL Image во временный файл и возвращает путь

    Args:
        image: PIL Image объект
        card_name: Название карты для имени файла

    Returns:
        str: Путь к сохраненному файлу
    """
    # Очищаем имя для имени файла
    clean_name = card_name.replace(' ', '_').replace('/', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tarot_{clean_name}_{timestamp}.png"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    # Сохраняем изображение
    image.save(filepath, format='PNG')

    return filepath


def save_images_to_temp(images: List[Image.Image], cards_data: List[Dict[str, Any]]) -> List[str]:
    """
    Сохраняет список изображений во временные файлы

    Args:
        images: Список PIL Image объектов
        cards_data: Список данных карт для получения имен

    Returns:
        List[str]: Список путей к сохраненным файлам
    """
    filepaths = []

    for i, (image, card_data) in enumerate(zip(images, cards_data)):
        # Получаем имя карты для файла
        card_name = card_data.get('name_en', f"card_{i + 1}")
        filepath = save_image_to_temp(image, card_name)
        filepaths.append(filepath)

    return filepaths


# ============================================
# ФУНКЦИЯ ДЛЯ ФОРМИРОВАНИЯ ТЕКСТА КАРТЫ
# ============================================

def format_card_text(card_data: Dict[str, Any], index: int, total: int) -> str:
    """
    Форматирует текст для одной карты

    Args:
        card_data: Словарь с данными карты от AI
        index: Индекс карты (для нумерации)
        total: Общее количество карт

    Returns:
        str: Отформатированный текст карты
    """
    position = card_data.get('position', f'Позиция {index + 1}')
    name_ru = card_data.get('name_ru', 'Неизвестная карта')
    orientation = card_data.get('orientation', 'Прямое')
    meaning = card_data.get('meaning', '')

    # Эмодзи для разных позиций (для красоты)
    emojis = ['🔮', '🃏', '🌟', '💫', '✨', '🌙', '☀️', '🕯️']
    emoji = emojis[index % len(emojis)]

    # Формируем текст
    text = f"""
{emoji} <b>{position}</b>

<b>Карта:</b> {name_ru}
<b>Ориентация:</b> {orientation}

<i>{meaning}</i>
"""
    return text.strip()


def format_main_message(ai_response: Dict[str, Any], user_name: str = "") -> str:
    """
    Формирует главное сообщение с интерпретацией, советом и ключевым посланием

    Args:
        ai_response: Полный ответ от AI
        user_name: Имя пользователя

    Returns:
        str: Отформатированное главное сообщение
    """
    interpretation = ai_response.get('interpretation', '')
    advice = ai_response.get('advice', '')
    key_message = ai_response.get('key_message', '')

    # Приветствие
    greeting = f"🔮 <b>Ваш расклад{' для ' + user_name if user_name else ''}</b>\n\n" if user_name else "🔮 <b>Ваш расклад</b>\n\n"

    # Основной текст
    parts = [greeting]

    if interpretation:
        parts.append(f"<b>📖 Интерпретация:</b>\n{interpretation}\n")

    if advice:
        parts.append(f"<b>💡 Совет:</b>\n{advice}\n")

    if key_message:
        parts.append(f"<b>✨ Ключевое послание:</b>\n<i>{key_message}</i>")

    return "\n".join(parts)


def format_upsell_text(intro: str, questions: list[str]) -> str:
    """
    Форматирует текст с вопросами в виде нумерованного списка
    """
    questions_text = "\n".join([f"{i + 1}. {q}" for i, q in enumerate(questions)])

    return f"""
{intro}

<b>Выберите вопрос:</b>

{questions_text}
"""


# ============================================
# ОСНОВНАЯ ФУНКЦИЯ СБОРКИ СООБЩЕНИЙ
# ============================================

def build_packed_messages(
        ai_response: Dict[str, Any],
        images: List[Image.Image],  # Теперь принимает список PIL Image
        user_name: str = ""
) -> PackedMultiMessage:
    """
    Собирает все сообщения в структуру PackedMultiMessage

    Args:
        ai_response: Ответ от AI (распарсенный JSON)
        images: Список PIL Image объектов
        user_name: Имя пользователя

    Returns:
        PackedMultiMessage: Готовые сообщения для отправки
    """
    cards_data = ai_response.get('cards', [])

    # 1. Формируем главное сообщение
    main_text = format_main_message(ai_response, user_name)

    # 2. Сохраняем изображения во временные файлы
    image_paths = save_images_to_temp(images, cards_data)

    # 3. Формируем сообщения для каждой карты
    card_messages = []

    for i, (card_data, image_path) in enumerate(zip(cards_data, image_paths)):
        card_text = format_card_text(card_data, i, len(cards_data))

        card_message = CardMessage(
            text=card_text,
            image=image_path  # Теперь это строка (путь к файлу)
        )
        card_messages.append(card_message)

    # 4. Собираем всё вместе
    return PackedMultiMessage(
        text=main_text,
        card_messages=card_messages
    )


def build_upsell_messages(ai_response: dict) -> UpSellMessage:
    intro = ai_response.get('intro')
    questions: list[str] = ai_response.get('questions')
    text = format_upsell_text(intro, questions)

    keyboard = []
    row = []
    for i in range(len(questions)):
        row.append(InlineKeyboardButton(text=str(i + 1), callback_data=f'question_{i}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    return UpSellMessage(
        text=text,
        keyboard=InlineKeyboardMarkup(inline_keyboard=keyboard),
        questions=questions
    )


def validate_ai_response(ai_response: Dict[str, Any]) -> bool:
    """
    Проверяет, что ответ AI содержит все необходимые поля

    Args:
        ai_response: Ответ от AI

    Returns:
        bool: True если все поля присутствуют
    """
    # Проверяем основные поля
    required_fields = ['cards', 'interpretation', 'advice', 'key_message']
    for field in required_fields:
        if field not in ai_response:
            logger.error(f'Отсутствует обязательное поле: {field}')
            return False

    # Проверяем карты
    cards = ai_response.get('cards', [])
    if len(cards) != 3:
        logger.error(f'Должно быть 3 карты, получено: {len(cards)}')
        return False

    # Проверяем каждую карту
    required_card_fields = ['position', 'name_ru', 'name_en', 'orientation', 'meaning']
    for i, card in enumerate(cards):
        for field in required_card_fields:
            if field not in card:
                logger.error(f'У карты {i + 1} отсутствует поле: {field}')
                return False

    return True


# ============================================
# ФУНКЦИЯ ДЛЯ ОЧИСТКИ ВРЕМЕННЫХ ФАЙЛОВ
# ============================================

def cleanup_images(image_paths: List[str]) -> None:
    """
    Удаляет временные файлы изображений

    Args:
        image_paths: Список путей к файлам для удаления
    """
    for filepath in image_paths:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"Удален временный файл: {filepath}")
        except Exception as e:
            logger.warning(f"Не удалось удалить файл {filepath}: {e}")


def cleanup_packed_messages(packed_messages: PackedMultiMessage) -> None:
    """
    Удаляет все временные файлы из PackedMultiMessage

    Args:
        packed_messages: PackedMultiMessage с путями к файлам
    """
    image_paths = [msg.image for msg in packed_messages.card_messages]
    cleanup_images(image_paths)


def validate_upsell_response(data: Dict[str, Any]) -> bool:
    """
    Проверяет, что ответ AI для допродажи содержит все необходимые поля

    Args:
        data: Ответ от AI (распарсенный JSON)

    Returns:
        bool: True если все поля присутствуют и валидны
    """
    # 1. Проверяем наличие основных полей
    required_fields = ['intro', 'questions']
    for field in required_fields:
        if field not in data:
            logger.error(f'Отсутствует обязательное поле: {field}')
            return False

    # 2. Проверяем intro (должен быть непустой строкой)
    intro = data.get('intro', '')
    if not intro or not isinstance(intro, str):
        logger.error('Поле "intro" должно быть непустой строкой')
        return False

    if len(intro) < 10:
        logger.warning('Поле "intro" слишком короткое')
        return False

    # 3. Проверяем questions (должен быть списком)
    questions = data.get('questions', [])
    if not isinstance(questions, list):
        logger.error('Поле "questions" должно быть списком')
        return False

    # 4. Проверяем количество вопросов (от 3 до 5)
    if len(questions) < 3:
        logger.error(f'Слишком мало вопросов: {len(questions)}. Должно быть от 3 до 5')
        return False

    if len(questions) > 5:
        logger.warning(f'Слишком много вопросов: {len(questions)}. Рекомендуется 3-5')
        # Не блокируем, но предупреждаем

    # 5. Проверяем каждый вопрос
    for i, question in enumerate(questions):
        if not isinstance(question, str):
            logger.error(f'Вопрос {i + 1} должен быть строкой, получено: {type(question)}')
            return False

        if not question or len(question.strip()) < 5:
            logger.error(f'Вопрос {i + 1} слишком короткий или пустой')
            return False

        if len(question) > 200:
            logger.warning(f'Вопрос {i + 1} слишком длинный: {len(question)} символов')
            # Не блокируем, но предупреждаем

    # 6. Проверяем уникальность вопросов
    unique_questions = set(questions)
    if len(unique_questions) != len(questions):
        logger.warning('Обнаружены повторяющиеся вопросы')
        # Не блокируем, но предупреждаем

    return True
