from dataclasses import dataclass
from enum import StrEnum
from functools import partial
from typing import Any, Coroutine

import httpx

from auction_transformers.translator import AzureTranslator, translate_auction
from models.auction import Auction


class TranslateLanguage(StrEnum):
    ENGLISH = 'en'
    SPANISH = 'es'
    ITALIAN = 'it'
    JAPANESE = 'ja'


@dataclass
class Translate:
    translate_titles: bool = True

    @staticmethod
    def translate_from(language: TranslateLanguage) -> partial[Coroutine[Any, Any, Auction]]:
        return partial(
            translate_auction,
            translator=AzureTranslator(client=httpx.AsyncClient()),
            translate_to=TranslateLanguage.ENGLISH,
            translate_from=language.value
        )
