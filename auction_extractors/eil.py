import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from app.models import AuctionExtractor, Auction


class EIL(AuctionExtractor):
    search_term: str

    @property
    def search_link(self) -> str:
        return f'https://eil.com/shop/artistlist.asp?page=1&sort=6&artistname={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'EIL'

    def get_auctions(self) -> List[Auction]:
        url = 'https://eil.com/shop/artistlist.asp'
        params = {
            'page': 1,
            'sort': 6,
            'artistname': {self.search_term}
        }

        r = requests.get(url=url, params=params)
        soup = BeautifulSoup(r.text, features='html.parser')
        print(r.url)
        auctions = []

        items = soup.find_all(name='table', attrs={'width': 180})
        for item in items:
            link = 'https://eil.com' + item.select_one('a')['href']
            image_link = item.select_one('img')['src'].replace('180x180', 'large_image')
            auction_id = link.split('=')[-1]
            _desc = item.select_one('font').getText(strip=True, separator='\n')
            _long_desc = ' '.join(item.select_one('a')['title'].split())
            description = f'{_desc}\n\n{_long_desc}'
            title = _desc.replace('\n', ' ').split(' In Stock')[0]

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                    start_date=datetime.datetime.now()
                )
            )

        return auctions
