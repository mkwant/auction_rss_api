from abc import abstractmethod
from datetime import datetime

from typing import List

from models import AuctionSearchResponse, Auction
from pydantic import BaseModel


class AuctionExtractor(BaseModel):
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
    def get_auctions(self) -> List[Auction]:
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
        return [Auction(auction_id='ERROR',
                        description=error,
                        link=self.search_link,
                        title="ERROR: Auctions couldn't be retrieved.",
                        start_date=datetime.now()
                        )]

    def search(self) -> AuctionSearchResponse:
        """
        Creates an AuctionSearchResponse item, which contains all the information needed to build an RSS feed.
        :return: An instance of AuctionSearchResponse
        """
        try:
            auctions = self.get_auctions()
        except Exception as e:
            auctions = self.auctions_on_error(
                error=f'Received this error when trying to retrieve the feed items: \n{e}')

        if len(auctions) == 0:
            auctions = self.auctions_on_error(error='No auctions were retrieved from the site.')

        return AuctionSearchResponse(
            search_link=self.search_link,
            search_term=self.search_term,
            site_desc=self.site_desc,
            auctions=auctions
        )


class AuctionExtractorAsync(BaseModel):
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
        return [Auction(auction_id='ERROR',
                        description=error,
                        link=self.search_link,
                        title="ERROR: Auctions couldn't be retrieved.",
                        start_date=datetime.now()
                        )]

    async def search(self) -> AuctionSearchResponse:
        """
        Creates an AuctionSearchResponse item, which contains all the information needed to build an RSS feed.
        :return: An instance of AuctionSearchResponse
        """
        try:
            auctions = await self.get_auctions()
        except Exception as e:
            auctions = self.auctions_on_error(
                error=f'Received this error when trying to retrieve the feed items: \n{e}')

        if len(auctions) == 0:
            auctions = self.auctions_on_error(error='No auctions were retrieved from the site.')

        return AuctionSearchResponse(
            search_link=self.search_link,
            search_term=self.search_term,
            site_desc=self.site_desc,
            auctions=auctions
        )
