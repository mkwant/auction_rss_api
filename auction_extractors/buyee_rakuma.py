from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


# TODO Translate titles -> make async

class BuyeeRakuma(AuctionExtractor):
    search_term: str

    @staticmethod
    def _get_auctions() -> ResultSet:
        url = 'https://buyee.jp/rakuma/search'
        params = {
            'keyword': 'bowie',
            'status': 'all'
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}

        r = requests.get(url=url, params=params, headers=headers)

        soup = BeautifulSoup(r.content, 'html.parser')
        return soup.select('ul.item-lists > li')

    def search(self) -> AuctionSearchResponse:
        auctions = []

        for item in self._get_auctions():
            title = item.select_one('h2.name').text
            description = f"{item.select_one('p.price').text} {item.select_one('p.price-fx').text}"
            _link = item.select_one('a')['href'].split('?')[0]
            link = f'https://buyee.jp{_link}'
            auction_id = _link.split('/')[-1]
            _image_link = item.select_one('img')['data-bind'].replace('\n', ' ').split('\'')[1].replace('/s/', '/l/')
            image_link = f"https{_image_link}"

            auctions.append(Auction(auction_id=auction_id,
                                    description=description,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    start_date=datetime.now()
                                    ))

        return AuctionSearchResponse(
            search_link=f'https://buyee.jp/rakuma/search?keyword={self.search_term}&status=all',
            search_term=self.search_term,
            site_desc=f'Buyee (Rakuma)',
            auctions=auctions
        )
