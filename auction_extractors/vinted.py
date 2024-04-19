from datetime import datetime
from typing import List, Optional

import requests

from models.auctionextractor import AuctionExtractor
from models.auction import Auction


class Vinted(AuctionExtractor):
    search_term: str
    catalog_id: Optional[int] = None

    @property
    def site_desc(self) -> str:
        return 'Vinted'

    @property
    def search_link(self) -> str:
        url = f'https://www.vinted.nl/catalog?search_text={self.search_term}'
        if self.catalog_id is not None:
            url += '&catalog[]={self.catalog_id}'
        return url

    def _get_page(self) -> List[dict]:
        url = 'https://www.vinted.nl/api/v2/catalog/items?'
        params = {
            'page': 1,
            'per_page': 96,
            'search_text': self.search_term
        }
        if self.catalog_id is not None:
            params['catalog_ids'] = self.catalog_id

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}

        s = requests.Session()
        s.headers.update(headers)
        # Retrieving cookie
        s.get(url='https://www.vinted.nl')

        r = s.get(url=url, params=params)
        return r.json()['items']

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in self._get_page():
            description = (f"{item['currency'].capitalize()} {float(item['price']):.2f}"
                           f" (+{float(item['service_fee']):.2f} service)")

            auctions.append(
                Auction(
                    title=item['title'],
                    auction_id=str(item['id']),
                    description=description,
                    link=item['url'],
                    image_link=item['photo']['full_size_url'],
                    seller=item['user']['login'],
                    start_date=datetime.now()
                )
            )

        return auctions
