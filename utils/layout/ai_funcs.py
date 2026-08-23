import httpx
import asyncio
import base64

from anthropic import AsyncAnthropic

from config_data.config import Config, load_config

config: Config = load_config()


client = AsyncAnthropic(
    api_key=config.apimart.api_key,
    base_url="https://api.apimart.ai"
    # http_client=
)


async def get_ai_answer(prompt: str | list[dict], system_prompt: str | None = None, image_base64: str = None):
    if isinstance(prompt, str):
        if not image_base64:
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
    else:
        messages = prompt
    message = await client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2048,
        system=system_prompt if system_prompt else None,
        messages=messages
    )
    return message.content[0].text