from datetime import datetime
from typing import List

import curl_cffi

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class CataWiki(AuctionExtractor):
    search_term: str

    @property
    def search_link(self) -> str:
        return f'https://www.catawiki.com/en/s?q={self.search_term}&sort=published_at_desc'

    @property
    def site_desc(self) -> str:
        return "Catawiki"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.catawiki.com/buyer/api/v1/search'
        params = {
            'q': {self.search_term},
            'page': 1,
            'sort': 'published_at_desc'
        }

        r = curl_cffi.get(url=url, params=params, impersonate='firefox')
        r.raise_for_status()

        lots = r.json()['lots']

        for auction in lots:
            auctions.append(
                Auction(
                    auction_id=str(auction['id']),
                    title=auction['title'],
                    link=auction['url'],
                    image_link=auction['originalImageUrl'],
                    start_date=datetime.fromisoformat(auction['biddingStartTime']),
                    description=auction['subtitle']
                )
            )

        return auctions
