import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class Discords(AuctionExtractor):
    search_term: str
    SITE = 'https://discords.nl'
    URL = f'{SITE}/collections/vendors'

    def _get_items(self) -> ResultSet:
        params = {'q': self.search_term,
                  'sort_by': 'created-descending'}

        r = requests.get(url=self.URL, params=params)
        soup = BeautifulSoup(r.content, 'html.parser')

        items = soup.find_all('div', {'class': 'product-item product-item--vertical 1/3--tablet 1/4--lap-and-up'})
        return items

    def search(self) -> AuctionSearchResponse:
        items = []

        for item in self._get_items():
            item_id = item.find('input', {'name': 'id'})['value']
            _product_info = item.find('a', {'class': 'product-item__title text--strong link'})
            print(item)
            item_url = f"{self.SITE}{_product_info['href']}"
            title = _product_info.get_text().strip()
            try:
                _inventory = item.find('span',
                                   {'class': re.compile('product-item__inventory inventory.*')}).get_text().strip()
            except AttributeError:
                _inventory = ''
            _price = item.find('span', {'class': 'price'}).get_text(separator=' ', strip=True).split(' ')[1]
            description = '\n'.join([_price, _inventory])
            image_url = f"https:{item.find_all('img')[-1]['src']}"

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
