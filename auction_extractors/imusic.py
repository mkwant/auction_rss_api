from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Imusic(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://imusic.co/page/search?_form=searchForm&advanced=1&combined={self.search_term}&sort=releaseDateDesc"

    @property
    def site_desc(self) -> str:
        return "Imusic"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://imusic.co/page/search'
        params = {
            '_form': 'searchForm',
            'advanced': 1,
            'combined': self.search_term,
            'sort': 'releaseDateDesc',
        }
        r = httpx.get(url=url, params=params)
        soup = BeautifulSoup(r.text, features='html.parser')
        items = soup.select('div.media')
        for item in items:
            _slug = item.select_one('a')['href']
            auction_id = _slug.split('/')[2]
            link = 'https://imusic.co' + _slug
            image_link = item.select_one('img')['src'].replace('scaled', 'original')
            title = item.select_one('a')['title']

            _price = item.select_one('button.price').text.strip()
            _note = item.select_one('button.btn-success[title]')['title']
            description = f'{_price}\n\n{_note}'

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
