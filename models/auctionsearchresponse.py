from datetime import datetime
from typing import List

from fastapi_rss import RSSResponse, GUID, Enclosure, EnclosureAttrs, Item, RSSFeed
from pydantic import BaseModel

from models.auction import Auction


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
            'title': title,
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
