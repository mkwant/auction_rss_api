import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class Discords(AuctionExtractor):
    search_term: str
    SITE: str = 'https://discords.nl'
    URL: str = f'{SITE}/collections/vendors'

    def _get_items(self) -> ResultSet:
        params = {'q': self.search_term,
                  'sort_by': 'created-descending'}

        r = requests.get(url=self.URL, params=params)
        soup = BeautifulSoup(r.content, features='html.parser')
        items = soup.select('div.product-item')
        return items

    def search(self) -> AuctionSearchResponse:
        items = []

        for item in self._get_items():
            item_id = item.select_one('input[name=id]')['value']
            _product_info = item.select_one('a.product-item__title')
            item_url = f"{self.SITE}{_product_info['href']}"
            title = _product_info.text.strip()
            try:
                _inventory = item.select_one('span.inventory').text.strip()
            except AttributeError:
                _inventory = ''
            _price = item.select_one('span.price').get_text(separator='|', strip=True).split('|')[1]
            description = '\n'.join([_price, _inventory])
            image_url = f"https:{item.select_one('img:last-child')['src']}"

            items.append(Auction(auction_id=item_id,
                                 description=description,
                                 image_link=image_url,
                                 link=item_url,
                                 title=title,
                                 start_date=datetime.now()
                                 ))

        return AuctionSearchResponse(
            search_link=f'{self.URL}?q={self.search_term}&sort_by=created-descending',
            search_term=self.search_term,
            site_desc=f'Discords',
            auctions=items
        )


if __name__ == '__main__':
    d = Discords(search_term='david bowie')
    d.search()