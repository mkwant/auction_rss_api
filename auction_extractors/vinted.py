from typing import List, Optional

import cloudscraper as cloudscraper

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Vinted(AuctionExtractor):
    search_term: str
    catalog_id: Optional[int] = None
    search_title_only: bool = True

    @property
    def site_desc(self) -> str:
        return 'Vinted'

    @property
    def search_link(self) -> str:
        url = f'https://www.vinted.nl/catalog?search_text={self.search_term}&order=newest_first'
        if self.catalog_id is not None:
            url += f'&catalog[]={self.catalog_id}'
        return url

    def _get_page(self) -> List[dict]:
        url = 'https://www.vinted.nl/api/v2/catalog/items?'
        params = {
            'page': 1,
            'per_page': 48,
            'search_text': self.search_term,
            'order': 'newest_first'
        }
        if self.catalog_id is not None:
            params['catalog_ids'] = self.catalog_id

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}
        s = cloudscraper.create_scraper()
        s.headers.update(headers)

        # Retrieving cookie
        s.get(url='https://www.vinted.nl')

        # Retrieving items
        r = s.get(url=url, params=params)
        print(r.text)
        r.raise_for_status()
        return r.json()['items']

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in self._get_page():
            from rich import print
            print(item)
            _currency = item['price']['currency_code'].capitalize()
            _amount = float(item['price']['amount'])
            _service_fee_currency = item['service_fee']['currency_code'].capitalize()
            _service_fee_amount = float(item['service_fee']['amount'])

            description = f"{_currency} {_amount:.2f} (+ {_service_fee_currency} {_service_fee_amount:.2f})"

            # Skip items if search term not in title
            if self.search_title_only:
                if self.search_term.lower() not in item['title'].lower():
                    continue

            auctions.append(
                Auction(
                    title=item['title'],
                    auction_id=str(item['id']),
                    description=description,
                    link=item['url'],
                    image_link=item['photo']['full_size_url'],
                    seller=item['user']['login']
                )
            )

        return auctions
