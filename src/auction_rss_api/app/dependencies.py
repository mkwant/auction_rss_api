from dataclasses import dataclass
from enum import StrEnum
from functools import partial
from typing import Any, Coroutine

import httpx2
from fastapi import Request

from auction_rss_api.auction_transformers.translator import (
    AzureTranslator,
    translate_auction,
)
from auction_rss_api.models.auction import Auction


class TranslateLanguage(StrEnum):
    ENGLISH = "en"
    SPANISH = "es"
    ITALIAN = "it"
    JAPANESE = "ja"


@dataclass
class Translate:
    client: httpx2.AsyncClient
    translate_titles: bool = True

    def translate_from(
        self,
        language: TranslateLanguage,
    ) -> partial[Coroutine[Any, Any, Auction]]:
        return partial(
            translate_auction,
            translator=AzureTranslator(client=self.client),
            translate_to=TranslateLanguage.ENGLISH,
            translate_from=language.value,
        )


async def get_browser(request: Request):
    return request.app.state.browser


async def get_translate(request: Request, translate_titles: bool = True) -> Translate:
    return Translate(client=request.app.state.http_client, translate_titles=translate_titles)
