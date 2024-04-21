import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Awaitable

from pydantic.dataclasses import dataclass

# from models.auctionextractor import Transformer
from models.auction import Auction
from models.auctionsearchresponse import AuctionSearchResponse

Transformer = Callable[[Auction], Awaitable[Auction]]

logger = logging.getLogger(__name__)


@dataclass
class SearchResponseTransformer(ABC):
    search_response: AuctionSearchResponse
    auction_transformers: Optional[List[Transformer]] = None

    @abstractmethod
    def transform(self) -> AuctionSearchResponse:
        ...


class ExcludeSellerName(SearchResponseTransformer):
    """If search_term in seller name and not in title, discard the auction."""

    def transform(self) -> AuctionSearchResponse:
        new_auction_list = []
        for auction in self.search_response.auctions:
            if search_term.lower() in auction.seller.lower() and \
                    self.search_response.search_term.lower() not in auction.title.lower:
                logger.debug(f"Discarded auction '{auction.title}' as {search_term=} in {auction.seller=} "
                             f"but not in {auction.title=}")
                continue
            else:
                new_auction_list.append(auction)
        self.search_response.auctions = new_auction_list
        return self.search_response
