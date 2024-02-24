import uuid
from dataclasses import dataclass
from typing import Optional

import httpx

from src.app.settings import settings


@dataclass
class Translate:
    translate_titles: bool = True


async def translate_text(
        client: httpx.AsyncClient,
        text: str,
        translate_to: str,
        translate_from: Optional[str] = None,
        ms_translate_api_key: str = settings.ms_translate_api_key,
        ms_translate_api_location: str = settings.ms_translate_api_location,
        api_version: float = '3.0'
) -> str:
    base_url = 'https://api.cognitive.microsofttranslator.com'
    endpoint = 'translate'
    headers = {
        'Ocp-Apim-Subscription-Key': ms_translate_api_key,
        'Ocp-Apim-Subscription-Region': ms_translate_api_location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    params = {
        'api-version': api_version,
        'to': translate_to
    }
    payload = [
        {
            'text': text
        }
    ]

    if translate_from:
        params['from'] = translate_from

    r = await client.post(
        url=f'{base_url}/{endpoint}',
        headers=headers,
        params=params,
        json=payload
    )
    try:
        result = r.json()[0]['translations'][0]['text']
    except Exception:
        raise ConnectionError(f'{r.json()}')
    return result
