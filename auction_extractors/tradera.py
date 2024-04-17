import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from app.models import AuctionExtractor, Auction


class Tradera(AuctionExtractor):
    search_term: str

    @property
    def search_link(self) -> str:
        return f'https://www.tradera.com/en/search?q={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'Tradera'

    def get_auctions(self) -> List[Auction]:
        url = 'https://www.tradera.com/en/search'
        params = {
            'q': self.search_term
        }
        cookies = {
            'preferred_currency': 'EUR',
            'Srp_Item_Layout': 'layout-list'
        }

        r = requests.get(url=url, params=params, cookies=cookies)
        soup = BeautifulSoup(r.text, features='html.parser')
        items = soup.select('div.item-card-new')

        auctions = []

        for item in items:
            link = 'https://www.tradera.com' + item.select_one('a')['href']
            image_link = item.select_one('img')['src']
            title = item.select_one('a')['title']
            auction_id = item['id'].split('-')[-1]
            _price = ' '.join([x.text for x in item.select('p.text-nowrap')])
            try:
                _endtime = item.select_one('span.item-card-animate-time').text
                description = f'{_price}\n{_endtime}'
            except AttributeError:
                description = f'Buy now {_price}'
            seller = item.select_one('span.item-card-list-detail-spaced').getText(strip=True, separator=' ')

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                    seller=seller,
                    start_date=datetime.datetime.now()
                )
            )
        return auctions
