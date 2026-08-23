import logging
import json

from utils.clean_json import _clean_json_response
from utils.layout.ai_funcs import get_ai_answer
from utils.layout.collect_messages import build_upsell_messages, validate_upsell_response
from constants import UPSELL_USER_PROMPT, UPSELL_SYSTEM_PROMPT
from gen_types import UpSellMessage, PackedMultiMessage


logger = logging.getLogger(__name__)


async def get_upsell_message(multi_message: PackedMultiMessage) -> UpSellMessage | None:
    """
    1. сообщение пользователя
    2. ответ ИИ
    3. новый промпт
    ! новый системный промпт
    """
    messages = []
    for msg in multi_message.messages:
        messages.append(
            {
                'role': msg.role,
                'content': msg.content
            }
        )

    messages.append(
        {
            'role': 'user',
            'content': UPSELL_USER_PROMPT
        }
    )

    try:
        result = await get_ai_answer(messages, UPSELL_SYSTEM_PROMPT)
    except Exception as err:
        logger.error(f'Generation Error: {err}')
        return None
    result = _clean_json_response(result)
    try:
        result_json = json.loads(result)
    except Exception as err:
        logger.error(f'Json loads Error')
        return None

    if not validate_upsell_response(result_json):
        logger.error('Ошибка валидации ответа Ai')
        return None

    messages = build_upsell_messages(result_json)
    return messages
