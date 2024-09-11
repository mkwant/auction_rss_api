import json
from typing import List

import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class HHV(AuctionExtractor):
    search_term: str

    @property
    def search_link(self) -> str:
        return f'https://www.hhv.de/shop/en/search/i:N5ST1?term={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'HHV (2nd hand)'

    def get_auctions(self) -> List[Auction]:

        url = 'https://www.hhv.de/shop/en/search/i:N5ST1?term=bowie'
        params = {'term': self.search_term}
        r = requests.get(url=url, params=params)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, features='html.parser')

        jsons = soup.find_all(name='script', attrs={'type': 'application/ld+json'})

        items = []

        for json_str in jsons[1:]:
            item = json.loads(json_str.text)[0]

            link = item['offers'][0]['url']
            image_link = item['image']
            title = item['description'].split('"')[1]
            item_id = item['sku']
            _currency = item['offers'][0]['priceCurrency']
            _price = item['offers'][0]['price']
            _brand = item['brand']['name']
            try:
                _catno = item['mpn']
            except KeyError:
                _catno = item['gtin']
            description = f"{_currency} {_price}\n{_brand} {_catno}"

            items.append(
                Auction(
                    auction_id=item_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title
                )
            )

        return items
