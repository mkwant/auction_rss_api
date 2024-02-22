from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import Auction


class RecordMecca(AuctionExtractor):
    search_term: str

    @property
    def site_desc(self) -> str:
        return 'RecordMecca'

    @property
    def search_link(self) -> str:
        return f'https://recordmecca.com?s={self.search_term}'

    def _get_auctions(self) -> ResultSet:
        url = 'https://recordmecca.com'
        params = {'s': self.search_term}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'}

        r = requests.get(url=url, params=params, headers=headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.content, 'html.parser')
        items = soup.select('div.default_product_display')
        return items

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in self._get_auctions():
            title = item.select_one('h2').get_text(strip=True)
            link = item.select_one('a')['href']
            image_link = item.select_one('img.featured_list_image')['src'].split('?')[0]
            _desc = item.select_one('div.wpsc_description').get_text(strip=True)
            _price = item.select_one('span.currentprice').get_text(strip=True)
            description = '\n'.join([_price, _desc])
            auction_id = link.split('/')[-2]

            auctions.append(Auction(auction_id=auction_id,
                                    description=description,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    start_date=datetime.now()
                                    ))

        return auctions
