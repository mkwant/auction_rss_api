import asyncio
import logging
import traceback
from abc import abstractmethod
from datetime import date, datetime
from typing import Awaitable, Callable, List

import nest_asyncio2
from fastapi_rss import RSSResponse
from pydantic import BaseModel, Field

from auction_rss_api.auction_transformers.html_linebreaks_in_desc import html_linebreaks_in_desc
from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionsearchresponse import AuctionSearchResponse

Transformer = Callable[[Auction], Awaitable[Auction]]

# Setting up logging
logger = logging.getLogger(__name__)

# To allow nested event loops. Should prevent 'event loop is closed' errors
nest_asyncio2.apply()


# TODO Create AuctionResponseTransformer ABC that can take an awaitable (or a func and use asyncio.to_thread?) to
#  transform Auction objects.

class AuctionExtractor(BaseModel):
    """
    A base class for an auction extractor.
    :param search_term: What to search for
    :param transformers: A list of transformers. A transformer is an Awaitable that takes and returns an Auction object.
                         Will be prepended to the default_transformers
    :param default_transformers: A list of transformers.

    """
    search_term: str | None = None
    transformers: List[Transformer] = Field(default_factory=list)
    default_transformers: List[Transformer] = Field(default_factory=lambda: [html_linebreaks_in_desc])

    @property
    @abstractmethod
    def search_link(self) -> str:
        """
        The link that shows the search result on the auction website.
        Will be used as the link property in the RSS feed.
        :return: A url.
        """
        ...

    @property
    @abstractmethod
    def site_desc(self) -> str:
        """
        A name for the site.
        Will be used as part of the description property of the RSS feed (followed by the search term).
        :return: A name for the site.
        """
        ...

    @abstractmethod
    def get_auctions(self) -> List[Auction]:
        """
        Return a list of the auctions from a search result
        :return: A list of Auction items.
        """
        ...

    def auctions_on_error(self, error_text: str, error: str) -> List[Auction]:
        """
        This will be returned when there is an error retrieving the auctions.
        :param error_text: The error text you want to display
        :param error: The error message
        :return: A list with one Auction record
        """
        logger.error(f"[{self.site_desc} ('{self.search_term}')] {error}: {error_text}")
        return [
            Auction(
                auction_id=f'ERROR_{date.today():%Y%m%d}',
                description=error,
                link=self.search_link,
                title=error_text,
                start_date=datetime.now()
            )
        ]

    def search(self) -> RSSResponse:
        """
        Creates an AuctionSearchResponse item, which contains all the information needed to build an RSS feed.
        :return: An instance of AuctionSearchResponse
        """
        try:
            auctions = self.get_auctions()
        except Exception as e:
            auctions = self.auctions_on_error(
                error_text="ERROR: Feed items couldn't be retrieved.",
                error=f'Received an error of type {type(e).__name__} when trying to retrieve the feed items: \n\n'
                      f'<pre>{traceback.format_exc()}</pre>'
            )

        logger.info(f"[{self.site_desc} ('{self.search_term}')] Retrieved {len(auctions)} entries.")
        if len(auctions) == 0:
            auctions = self.auctions_on_error(
                error_text="WARNING: No items were found.",
                error='No items were found when trying to retrieve the feed items.'
            )

        auction_search_response = AuctionSearchResponse(
            search_link=self.search_link,
            search_term=self.search_term,
            site_desc=self.site_desc,
            auctions=auctions,
        )

        # Apply the transformers to the auction search response
        async def transform():
            for transformer in self.transformers + self.default_transformers:
                statements = [transformer(x) for x in auctions]
                await asyncio.gather(*statements)

        asyncio.run(transform())

        return auction_search_response.to_rss()


class AuctionExtractorAsync(BaseModel):
    """A base class for an async auction extractor."""
    search_term: str

    @property
    @abstractmethod
    def search_link(self) -> str:
        """
        The link that shows the search result on the auction website.
        Will be used as the link property in the RSS feed.
        :return: A url.
        """
        ...

    @property
    @abstractmethod
    def site_desc(self) -> str:
        """
        A name for the site.
        Will be used as part of the description property of the RSS feed (followed by the search term).
        :return: A name for the site.

        """
        ...

    @abstractmethod
    async def get_auctions(self) -> List[Auction]:
        """
        Return a list of the auctions from a search result
        :return: A list of Auction items.
        """
        ...

    def auctions_on_error(self, error: str) -> List[Auction]:
        """
        This will be returned when there is an error retrieving the auctions.
        :param error: The error message
        :return: A list with one Auction record
        """
        return [
            Auction(
                auction_id='ERROR',
                description=error,
                link=self.search_link,
                title="ERROR: Feed items couldn't be retrieved.",
                start_date=datetime.now()
            )
        ]

    async def search(self) -> RSSResponse:
        """
        Creates an AuctionSearchResponse item, which contains all the information needed to build an RSS feed.
        :return: An instance of AuctionSearchResponse
        """
        try:
            auctions = await self.get_auctions()
        except Exception as e:
            auctions = self.auctions_on_error(
                error=f'Received an error of type {type(e).__name__} when trying to retrieve the feed items: \n\n'
                      f'<pre>{traceback.format_exc()}</pre>'
            )

        if len(auctions) == 0:
            auctions = self.auctions_on_error(
                error="""No items could be retrieved from the site.\n
                      This could be because the site is unavailable or because the site layout changed."""
            )

        auction_search_response = AuctionSearchResponse(
            search_link=self.search_link,
            search_term=self.search_term,
            site_desc=self.site_desc,
            auctions=auctions
        )

        return auction_search_response.to_rss()
