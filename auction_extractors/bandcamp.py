from typing import List

import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Bandcamp(AuctionExtractor):
    @property
    def base_url(self):
        return f'https://{self.search_term}.bandcamp.com'

    @property
    def search_link(self) -> str:
        return f'{self.base_url}/merch'

    @property
    def site_desc(self) -> str:
        return f'Bandcamp'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = requests.get(self.search_link)
        soup = BeautifulSoup(r.text, features='html.parser')
        item_list = soup.select_one('ol.merch-grid')
        items = item_list.select('li.merch-grid-item')

        for item in items:
            auction_id = item["data-item-id"]

            _title = ' '.join(
                ' '.join([x.strip() for x in item.select_one('p.title') if isinstance(x, str)]).strip().split())
            try:
                _artist = item.select_one('p.title>span.artist-override').text
                title = f'{_artist}: {_title}'
            except AttributeError:
                title = _title

            link = self.base_url + item.select_one('a')['href']

            try:
                image_link = item.select_one('img')['data-original']
            except KeyError:
                image_link = item.select_one('img')['src']
            image_link = image_link.replace('_37', '_10')

            _item_type = item.select_one('div.merchtype').text.strip()
            _price = item.select_one('p.price').text.strip()
            description = f'{_item_type}\n{_price}'

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link
                }))

        return auctions
