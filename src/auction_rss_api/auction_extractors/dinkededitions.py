from typing import List

import dateparser
import httpx

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class DinkedEditions(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://dinkededition.co.uk/editions'

    @property
    def site_desc(self) -> str:
        return "DinkedEditions"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url=f"{self.search_link}?format=json")
        r.raise_for_status()

        items = r.json()['items']

        auctions = []

        for item in items:
            unique_id = item['id']
            link = f"{self.search_link}/{item['urlId']}"
            image_link = item['assetUrl']
            title = f"{item['title']} ({item['categories'][0]})"
            published_date = dateparser.parse(str(item['publishOn']))
            description = item['body']

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    link=link,
                    image_link=image_link,
                    title=title,
                    description=description,
                    start_date=published_date,
                )
            )

        return auctions
