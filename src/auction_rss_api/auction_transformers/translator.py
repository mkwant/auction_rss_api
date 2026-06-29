import logging
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional

import httpx
import truststore
from asgi_correlation_id import correlation_id
from diskcache import Cache, JSONDisk

from auction_rss_api.app.settings import settings
from auction_rss_api.models.auction import Auction

truststore.inject_into_ssl()  # Use OS trust store

# Setting up logging
logger = logging.getLogger(__name__)


class Translator(ABC):
    """An abstract class that defines the interface for translating strings."""
    translate_to: str
    translate_from: str

    @abstractmethod
    async def translate(self, text: str, translate_to: str, translate_from: str | None) -> str:
        """Translate a string to another string."""
        raise NotImplementedError


class AzureTranslator(Translator):
    """Azure Translator."""
    api_version: str = '3.0'
    base_url = 'https://api.cognitive.microsofttranslator.com'
    endpoint = 'translate'

    CACHE_TTL = timedelta(days=90).total_seconds()

    def __init__(
            self,
            client: httpx.AsyncClient,
            ms_translate_api_key: str = settings.MS_TRANSLATE_API_KEY,
            ms_translate_api_location: str = settings.MS_TRANSLATE_API_LOCATION
    ) -> None:
        """Initialize the AzureTranslator."""
        self.client = client
        self.ms_translate_api_key = ms_translate_api_key
        self.ms_translate_api_location = ms_translate_api_location

        self.cache = Cache(
            directory="/.translation_cache",
            disk=JSONDisk,
        )

    async def translate(self, text: str, translate_from: str, translate_to: str) -> str:
        cache_key = f"{text}:{translate_from}:{translate_to}"

        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Translation cache hit, {cache_key=}")
            return cached

        headers = {
            'Ocp-Apim-Subscription-Key': self.ms_translate_api_key,
            'Ocp-Apim-Subscription-Region': self.ms_translate_api_location,
            'Content-type': 'application/json',
            'X-ClientTraceId': correlation_id.get()
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

        self.cache.set(
            key=cache_key,
            value=result,
            expire=self.CACHE_TTL,
        )

        logger.debug(f"Translated '{text}' to '{result}' ({translate_from=}, {translate_to=})")
        return result


async def translate_auction(
        auction: Auction,
        translator: Translator,
        translate_to: str,
        translate_from: Optional[str] = None
) -> Auction:
    """Translate the auction title using a translator. Append the original title to the description."""

    # Don't translate error items
    if auction.auction_id.startswith('ERROR_'):
        return auction

    original_title = auction.title
    try:

        translated_title = await translator.translate(
            text=auction.title,
            translate_to=translate_to,
            translate_from=translate_from
        )
    except Exception as e:
        logger.warning(
            f"Error translating {auction.title} ({translate_from=}, {translate_to=}): {e.__class__.__name__} '{e}'")
        auction.description = f"{auction.description}\n\nTranslate failed: '{e}'"
        return auction

    auction.title = translated_title
    auction.description = f"{auction.description}\n\nOriginal title: '{original_title}'"
    return auction

# azure_translator = AzureTranslator(client=httpx.AsyncClient())
# translate_from_jp = partial(translate_auction, translator=azure_translator, translate_to='en', translate_from='ja')
# translate_from_es = partial(translate_auction, translator=azure_translator, translate_to='en', translate_from='es')
