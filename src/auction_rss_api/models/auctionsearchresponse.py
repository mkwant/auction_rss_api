from datetime import datetime
from typing import List

from fastapi_rss import GUID, Enclosure, EnclosureAttrs, Item, RSSFeed, RSSResponse
from pydantic import BaseModel

from auction_rss_api.models.auction import Auction
from auction_rss_api import __name__, __version__


class AuctionSearchResponse(BaseModel):
    """The result from an auction search."""
    search_link: str
    search_term: str | None
    site_desc: str
    auctions: List[Auction]

    def to_rss(self) -> RSSResponse:
        """Return an RSSResponse that can be used as a FastApi response."""

        items = []

        if self.search_term is None:
            title = self.site_desc
        else:
            title = f"{self.site_desc} ('{self.search_term}')"

        for auction in self.auctions:

            if auction.image_link:
                enclosure = Enclosure(
                    content='',  # noqa, this field is needed due to a bug in fastapi_rss # ty: ignore[unknown-argument]
                    attrs=EnclosureAttrs(
                        url=auction.image_link,
                        length=1000,
                        type='image/jpeg'
                    )
                )
            else:
                enclosure = None

            items.append(
                Item(
                    title=auction.title,
                    link=auction.link,
                    description=auction.description,
                    guid=GUID(content=auction.auction_id),
                    author=auction.seller,
                    pub_date=auction.start_date,
                    enclosure=enclosure,
                )
            )

        # Instantiate the RSSFeed class
        feed = RSSFeed(
            title=title,
            link=self.search_link,
            description=f"Search results for query '{self.search_term}' on {self.site_desc}",
            language='en-us',
            generator=f'{__name__}/{__version__}',
            ttl=40,
            item=items,
            pub_date=datetime.now(),
            last_build_date=datetime.now()
        )

        # Return the RSSResponse
        return RSSResponse(content=feed)
