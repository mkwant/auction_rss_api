import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import httpx

from app.settings import settings


@dataclass
class Translate:
    translate_titles: bool = True


class Translator(ABC):
    translate_to: str
    translate_from: str

    @abstractmethod
    async def translate(self, text: str, translate_to: str, translate_from: str) -> str:
        raise NotImplementedError


class AzureTranslator(Translator):
    api_version: float = '3.0'
    base_url = 'https://api.cognitive.microsofttranslator.com'
    endpoint = 'translate'

    def __init__(
            self,
            client: httpx.AsyncClient,
            ms_translate_api_key: str = settings.ms_translate_api_key,
            ms_translate_api_location: str = settings.ms_translate_api_location
    ):
        self.client = client
        self.ms_translate_api_key = ms_translate_api_key
        self.ms_translate_api_location = ms_translate_api_location

    async def translate(self, text: str, translate_to: str, translate_from: str) -> str:
        headers = {
            'Ocp-Apim-Subscription-Key': self.ms_translate_api_key,
            'Ocp-Apim-Subscription-Region': self.ms_translate_api_location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        params = {
            'api-version': self.api_version,
            'to': translate_to
        }
        payload = [
            {
                'text': text
            }
        ]

        if translate_from:
            params['from'] = translate_from

        r = await self.client.post(
            url=f'{self.base_url}/{self.endpoint}',
            headers=headers,
            params=params,
            json=payload
        )
        try:
            result = r.json()[0]['translations'][0]['text']
        except Exception:
            raise ConnectionError(f'{r.json()}')
        return result
