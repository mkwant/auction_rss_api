import os
import uuid
from dataclasses import dataclass
from typing import Optional

import httpx

from app.settings import Settings

settings = Settings()


@dataclass
class Translate:
    translate_titles: bool = True


async def translate_text(
        client: httpx.AsyncClient,
        text: str,
        translate_to: str,
        ms_translate_api_key: str = settings.ms_translate_api_key,
        ms_translate_api_location: str = settings.ms_translate_api_location,
        api_version: float = '3.0'
) -> str:
    base_url = 'https://api.cognitive.microsofttranslator.com'
    endpoint = 'translate'

    url = f'{base_url}/{endpoint}?api-version={api_version}&to={translate_to}'

    headers = {
        'Ocp-Apim-Subscription-Key': ms_translate_api_key,
        'Ocp-Apim-Subscription-Region': ms_translate_api_location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    payload = [
        {
            'text': text
        }
    ]

    r = await client.post(url, headers=headers, json=payload)
    try:
        result = r.json()[0]['translations'][0]['text']
    except Exception:
        raise ConnectionError(f'{r.json()}')
    return result
