from datetime import datetime
from typing import List

import requests

from models.auctionextractor import AuctionExtractor
from models.auction import Auction


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

        url = f'https://www.catawiki.com/buyer/api/v1/search'
        params = {
            'q': {self.search_term},
            'page': 1,
            'sort': 'published_at_desc'
        }
        r = requests.get(url=url, params=params)

        for auction in r.json()['lots']:
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
