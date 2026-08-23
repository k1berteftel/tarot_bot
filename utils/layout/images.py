import os
import asyncio
import tempfile
import logging
from typing import List, Dict, Optional
from datetime import datetime

from arcanite.core import TarotDeck
from PIL import Image


logger = logging.getLogger(__name__)


class ArcaniteImageExtractor:
    """
    Класс для извлечения изображений карт из колоды arcanite
    """

    def __init__(self):
        """Инициализация с загрузкой колоды arcanite"""
        self.deck: TarotDeck | None = None
        self._load_deck()

    def _load_deck(self):
        """Загружает колоду из arcanite"""
        try:
            self.deck = TarotDeck.load()
            logger.info(f"✅ Колода загружена: {len(self.deck.cards)} карт")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки колоды: {e}")
            self.deck = None

    def get_card_image(self, card_name: str, orientation: str = "Прямое") -> Optional[Image.Image]:
        """
        Получает изображение карты из колоды arcanite

        Args:
            card_name: Название карты (например, "The Magician")
            orientation: "Прямое" или "Перевернутое"

        Returns:
            PIL Image объект или None
        """
        if not self.deck:
            logger.error("❌ Колода не загружена")
            return None

        try:
            # Ищем карту в колоде
            card = None
            for taro_card in self.deck.cards:
                if taro_card.card_name == card_name:
                    card = taro_card

            if card is None:
                logger.error(f"⚠️ Карта '{card_name}' не найдена в колоде")
                return None

            # Получаем изображение
            img = card.image_filename

            if not img:
                logger.error(f"⚠️ Не удалось получить изображение для '{card_name}'")
                return None

            img_path = 'images/' + img
            if not os.path.exists(img_path):
                logger.error(f"⚠️ Не удалось найти путь к изображению для '{card_name}'")
                return None
            img = Image.open(img_path)

            # Разворачиваем если перевернутая
            if orientation == "Перевернутое":
                img = img.rotate(180)

            return img

        except Exception as e:
            logger.error(f"⚠️ Ошибка получения карты '{card_name}': {e}")
            return None

    def get_spread_images(self, cards_data: List[Dict[str, str]]) -> List[Image.Image]:
        """
        Получает список изображений для расклада

        Args:
            cards_data: Список словарей с данными карт:
                [
                    {"name": "The Magician", "orientation": "Прямое"},
                    {"name": "The High Priestess", "orientation": "Перевернутое"}
                ]
        Returns:
            List[Image.Image]: Список изображений карт
        """
        images = []
        for card_data in cards_data:
            name = card_data.get('name_en', '')
            orientation = card_data.get('orientation', 'Прямое')

            img = self.get_card_image(name, orientation)
            if img:
                images.append(img)
            else:
                logger.warning(f"⚠️ Карта '{name}' не найдена, пропускаем")

        return images


def get_tarot_spread_images(
        cards_data: List[Dict[str, str]],
) -> list[Image]:
    """
    Упрощенная функция для получения всех карт расклада

    Args:
        cards_data: Список словарей с данными карт

    Returns:
        List[str] (пути к файлам) или List[Image] (PIL объекты)
    """
    extractor = ArcaniteImageExtractor()
    return extractor.get_spread_images(cards_data)

