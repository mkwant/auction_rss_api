from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class BuyeeMercari(AuctionExtractor):

    @property
    def search_link(self) -> str:
        return f"https://buyee.jp/mercari/search?limit=100&lang=en&page=1&searchType=filter&order-sort=desc-created_time&keyword={self.search_term}&currencyCode=EUR"

    @property
    def site_desc(self) -> str:
        return 'Buyee (Mercari)'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        link = 'https://buyee.jp/mercari/search'
        params = {
            'limit': 100,
            'keyword': self.search_term,
            'order-sort': 'desc-created_time',
            'currencyCode': 'EUR',
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0'}

        r = httpx.get(url=link, params=params, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')

        items = soup.select('ul.item-lists>li.list')
        for item in items:
            link = 'https://buyee.jp' + item.select_one('a')['href']
            auction_id = link.split('?')[0].split('/')[-1]
            _image_link = item.select_one('img')['data-bind'].replace('\n', ' ').split('\'')[1].replace('/small/',
                                                                                                        '/large/')
            image_link = f"https:{_image_link.split('?')[0]}"

            title = item.select_one('h2.name').text.strip()

            _price_yen = item.select_one('p.price').text.strip()
            _price_eur = item.select_one('p.price-fx').text.strip()
            try:
                _sold_out = item.select_one('div.soldOut__text').text.strip()
                description = f"{_sold_out}\n{_price_yen} {_price_eur}"
            except AttributeError:
                description = f"{_price_yen} {_price_eur}"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    link=link,
                    image_link=image_link,
                    title=title,
                    description=description,
                )
            )

        return auctions
