import asyncio
from abc import abstractmethod
from datetime import datetime
from typing import List, Optional

import httpx
from fastapi_rss import RSSResponse, GUID, Enclosure, EnclosureAttrs, Item, RSSFeed
from httpx import HTTPError
from pydantic import BaseModel

from dependencies.translate import translate_text


class Auction(BaseModel):
    """An auction model."""
    title: str
    auction_id: str
    description: str
    link: str
    image_link: Optional[str] = None
    seller: Optional[str] = None
    start_date: datetime


class AuctionSearchResponse(BaseModel):
    """The result from an auction search."""
    search_link: str
    search_term: str
    site_desc: str
    auctions: List[Auction]

    @staticmethod
    async def _translate_auction(
            client: httpx.AsyncClient,
            auction: Auction,
            translate_to: str,
            translate_from: Optional[str] = None
    ) -> Auction:
        """Translate the auction title. Append the original title to the description."""
        original_title = auction.title
        try:

            translated_title = await translate_text(
                client=client,
                text=auction.title,
                translate_to=translate_to,
                translate_from=translate_from
            )
        except (HTTPError, ConnectionError) as e:
            auction.description = f"{auction.description}\n\nTranslate failed: '{e}'"
            return auction

        auction.title = translated_title
        auction.description = f"{auction.description}\n\nOriginal title: '{original_title}'"
        return auction

    async def translate(self, translate_to: str = 'en', translate_from: Optional[str] = None):
        client = httpx.AsyncClient()
        statements = []
        for auction in self.auctions:
            # Don't translate error items
            if auction.auction_id == 'ERROR':
                continue
            statements.append(
                self._translate_auction(
                    translate_to=translate_to,
                    translate_from=translate_from,
                    auction=auction,
                    client=client
                )
            )
        await asyncio.gather(*statements)

    def to_rss(self) -> RSSResponse:
        """Return an RSSResponse that can be used as a FastApi response."""

        items = []

        for auction in self.auctions:

            item_data = {
                'title': auction.title,
                'link': auction.link,
                'description': auction.description,
                'guid': GUID(content=auction.auction_id),
                'author': auction.seller,
                'pub_date': auction.start_date
            }

            if auction.image_link:
                item_data['enclosure'] = Enclosure(
                    content='',
                    attrs=EnclosureAttrs(
                        url=auction.image_link,
                        length=1000,
                        type='image/jpeg'
                    )
                )
            items.append(Item(**item_data))

        # Instantiate the RSSFeed class
        feed_data = {
            'title': f"{self.site_desc} ('{self.search_term}')",
            'link': self.search_link,
            'description': f"Search results for query '{self.search_term}' on {self.site_desc}",
            'language': 'en-us',
            'generator': 'Auction RSS api',
            'ttl': 40,
            'item': items,
            'pub_date': datetime.now(),
            'last_build_date': datetime.now()
        }
        feed = RSSFeed(**feed_data)

        # Return the RSSResponse
        return RSSResponse(content=feed)


class AuctionExtractor(BaseModel):
    """A base class for an auction extractor."""
    search_term: str
    translate_titles: bool = False
    translate_from: Optional[str] = None

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
        return [
            Auction(
                auction_id='ERROR',
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
                error=f'Received this error when trying to retrieve the feed items: \n{e}'
            )

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

        if self.translate_titles:
            asyncio.run(auction_search_response.translate(translate_from=self.translate_from))

        # Replace line breaks in description for HTML breaks
        for auction in auctions:
            auction.description = auction.description.replace('\n', '<br>\n')

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
                error=f'Received this error when trying to retrieve the feed items: \n{e}'
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
