from typing import List

import requests
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class JapanRecords(AuctionExtractor):
    search_term: str

    @property
    def search_link(self) -> str:
        return f'https://japan-records.de/en/search?controller=search&s={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'japan-records.de'

    def get_auctions(self) -> List[Auction]:
        auctions = []
        r = requests.get(url=self.search_link)
        soup = BeautifulSoup(r.content, features='html.parser')
        items = soup.select('article.js-product')
        for item in items:
            title = item.select_one('h2.product-title').text
            _price = item.select_one('span.price').text.strip()
            _desc = item.select_one('div.product-detail').text.strip()
            description = '<br>'.join((_price, _desc))
            auction_id = item['data-id-product']
            link = item.select_one('h2.product-title>a')['href']
            image_link = item.select_one('img')['data-full-size-image-url']

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link
                )
            )

        # Sort by auction_id so the newest auctions are first
        auctions.sort(key=lambda auction: int(auction.auction_id), reverse=True)

        return auctions
