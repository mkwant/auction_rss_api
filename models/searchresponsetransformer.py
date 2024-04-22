import asyncio
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Callable, Awaitable

from auction_transformers.translator import translate_from_jp
# from pydantic.dataclasses import dataclass

# from models.auctionextractor import Transformer
from models.auction import Auction
from models.auctionsearchresponse import AuctionSearchResponse

Transformer = Callable[[Auction], Awaitable[Auction]]

logger = logging.getLogger(__name__)


@dataclass
class SearchResponseTransformer(ABC):
    search_response: AuctionSearchResponse

    auction_transformers: Optional[List[Transformer]] = None

    # @abstractmethod
    # def auction_transformers(self) -> Optional[List[Transformer]]:
    #     pass

    async def __post_init__(self):
        if self.auction_transformers:
            for transformer in self.auction_transformers:
                statements = [transformer(x) for x in self.search_response.auctions]
                await asyncio.gather(*statements)

    @abstractmethod
    def transform(self) -> AuctionSearchResponse:
        ...


class ExcludeSellerName(SearchResponseTransformer):
    """If search_term in seller name and not in title, discard the auction."""

    def transform(self) -> AuctionSearchResponse:
        new_auction_list = []
        for auction in self.search_response.auctions:
            if self.search_response.search_term.lower() in auction.seller.lower() and \
                    self.search_response.search_term.lower() not in auction.title.lower:
                logger.debug(f"Discarded auction '{auction.title}' as search_term={self.search_response.search_term} "
                             f"in {auction.seller=} but not in {auction.title=}")
                continue
            else:
                new_auction_list.append(auction)
        self.search_response.auctions = new_auction_list
        return self.search_response


class CleanControlCharacters(SearchResponseTransformer):
    """Clean control characters from auction title."""

    def transform(self) -> AuctionSearchResponse:
        for auction in self.search_response.auctions:
            auction.title = re.sub(
                pattern=u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+',
                repl='',
                string=auction.title
            )
            return self.search_response


class TranslateFromJp(SearchResponseTransformer):
    def auction_transformers(self) -> Optional[List[Transformer]]:
        return [translate_from_jp]

    def transform(self) -> AuctionSearchResponse:
        pass
