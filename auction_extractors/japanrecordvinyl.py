from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class JapanRecordVinyl(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://japan-record-vinyl.com/search?q={self.search_term}&filter.v.availability=1&sort_by=relevance"

    @property
    def site_desc(self) -> str:
        return "JapanRecordVinyl"

    def get_auctions(self) -> List[Auction]:
        url = 'https://japan-record-vinyl.com/search'
        params = {
            'q': self.search_term,
            'filter.v.availability': 1,
            'sort_by': 'relevance',
        }
        r = httpx.get(url=url, params=params)
        soup = BeautifulSoup(r.text, features='html.parser')

        auctions = []

        items = soup.select('article.product-card')
        for item in items:
            title = item.select_one('a.tw-text-color').text.strip()
            _slug = item.select_one('a.tw-text-color')['href']
            link = 'https://japan-record-vinyl.com' + _slug
            auction_id = _slug.split('/')[-1].split('?')[0]
            image_link = 'https:' + item.select_one('img.noscript-image')['src'].split('?')[0]
            desc = item.select_one('span.product-card-price').text.strip()

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=desc,
                )
            )

        return auctions
