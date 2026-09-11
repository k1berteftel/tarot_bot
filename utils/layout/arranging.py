import re
import json
import logging
from typing import Literal

from aiogram import Bot
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from utils.clean_json import _clean_json_response
from utils.layout.ai_funcs import get_ai_answer
from utils.layout.process_wrapper import wait_with_progress
from utils.layout.images import get_tarot_spread_images
from utils.layout.collect_messages import validate_ai_response, build_packed_messages, cleanup_packed_messages
from utils.layout.upsell import get_upsell_message
from gen_types import CardMessage, PackedMultiMessage, BaseAiMessage
from constants import SYSTEM_PROMPT, PROMPTS, ADDITIONAL_PROMPTS


logger = logging.getLogger(__name__)


def _get_result_prompt(data: dict, rate: str, first: bool = True) -> str:
    prompt_template = PROMPTS.get(rate) if first else ADDITIONAL_PROMPTS.get(rate)
    if rate == 'relation':
        prompt_data = {
            'name': data.get('name'),
            'birth_date': data.get('birthday').strftime("%d-%m-%Y"),
            'partner_name': data.get('partner_name'),
            'partner_birth_date': data.get('partner_birthday').strftime("%d-%m-%Y"),
            'situation': data.get('situation')
        }
    elif rate == 'old':
        prompt_data = {
            'name': data.get('name'),
            'birth_date': data.get('birthday').strftime("%d-%m-%Y"),
            'partner_name': data.get('partner_name'),
            'partner_birth_date': data.get('partner_birthday').strftime("%d-%m-%Y"),
            'situation': data.get('situation')
        }
    elif rate == 'finance':
        prompt_data = {
            'name': data.get('name'),
            'birth_date': data.get('birthday').strftime("%d-%m-%Y"),
            'activity': data.get('activity'),
            'financial_request': data.get('request'),
            'situation': data.get('situation')
        }
    elif rate == 'future':
        prompt_data = {
            'name': data.get('name'),
            'birth_date': data.get('birthday').strftime("%d-%m-%Y"),
            'life_area': data.get('sphere')
        }
        if first:
            prompt_data['user_question'] = data.get('purpose')
        else:
            prompt_data['user_question_original'] = data.get('purpose')
    else:  # question
        prompt_data = {}
        pass

    if first:
        prompt = prompt_template.format(**prompt_data)
    else:
        # rate == 'question'
        prompt_data['user_question'] = data.get('question')
        prompt = prompt_template.format(**prompt_data)
    return prompt


async def create_messages(form_data: dict, rate: str, context_messages: list[BaseAiMessage] | None) -> PackedMultiMessage | None:
    """
    :return: tuple[dict, PackedMultiMessage] | None, None в случае ошибки (попробовать позже)
    """
    # сборка промпта для расклада
    prompt = _get_result_prompt(form_data, rate, not bool(context_messages))
    if context_messages:
        messages = []
        for msg in context_messages:
            messages.append(
                {
                    'role': msg.role,
                    'content': msg.content
                }
            )
        messages.append(
            {
                'role': 'user',
                'content': prompt
            }
        )
        prompt = messages

    # процесс генерации расклада
    try:
        result = await get_ai_answer(prompt, SYSTEM_PROMPT)
    except Exception as err:
        logger.error(f'Generation Error: {err}')
        return None
    result = _clean_json_response(result)
    try:
        result_json = json.loads(result)
    except Exception as err:
        logger.error(f'Json loads Error: {err}')
        return None

    if not validate_ai_response(result_json):
        logger.error('Ошибка валидации ответа Ai')
        return None

    cards = result_json.get('cards', [])
    images = get_tarot_spread_images(cards)
    messages = build_packed_messages(result_json, images)
    messages.messages.append(BaseAiMessage(
        role='user',
        content=prompt
    ))
    messages.messages.append(BaseAiMessage(
        role='assistant',
        content=result
    ))
    return messages


async def process_arranging(form_data: dict, user_id: int, bot: Bot, context: FSMContext, messages: list[BaseAiMessage] = None):
    logger.info('Start arranging process')
    rate = form_data.get('rate')
    logger.info(f'Trying to create messages for rate "{rate}"')
    result = await create_messages(form_data, rate, context_messages=messages)
    logger.info(f'Messages created: {bool(result)}')
    progress_message = await wait_with_progress(user_id, bot, 10, 20)
    if not result:
        result = await create_messages(form_data, rate, context_messages=messages)
        if not result:
            try:
                await progress_message.delete()
            except Exception:
                ...
            await bot.send_message(
                chat_id=user_id,
                text='🚨Во время отправки сообщения произошла неизвестная ошибка, пожалуйста обратитесь в поддержку @vedymahelpbot'
            )
            return
    try:
        await progress_message.delete()
    except Exception:
        ...

    messages = result
    for card_message in messages.card_messages:
        image = FSInputFile(card_message.image)
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=image,
                caption=card_message.text
            )
        except Exception:
            ...
    try:
        await bot.send_message(
            chat_id=user_id,
            text=messages.text
        )
    except Exception:
        ...
    # отправка сообщений допродажи
    upsell_message = await get_upsell_message(messages)
    if not upsell_message:
        logger.error('Ошибка создания сообщения допродажи')
        return
    await context.update_data(questions=upsell_message.questions, ai_context=messages.messages, ai_data=form_data, init_rate=rate)
    try:
        await bot.send_message(
            chat_id=user_id,
            text=upsell_message.text,
            reply_markup=upsell_message.keyboard
        )
    except Exception:
        ...
