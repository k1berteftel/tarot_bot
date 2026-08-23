import re


def _clean_json_response(text: str) -> str:
    """Очищает ответ от markdown-разметки JSON"""
    # Убираем ```json и ``` в начале и конце
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    # Убираем любые другие markdown-блоки
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    return text.strip()