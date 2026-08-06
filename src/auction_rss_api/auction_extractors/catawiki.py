from datetime import datetime
from typing import List

import cloudscraper as cloudscraper

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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) Gecko/20100101 Firefox/153.0'}
        s = cloudscraper.create_scraper()
        s.headers.update(headers)

        r = s.get(url=url, params=params)
        r.raise_for_status()

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
