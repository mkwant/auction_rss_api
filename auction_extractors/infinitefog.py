from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class InfiniteFog(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://infinitefog.ru/shop/new?lang=en'

    @property
    def site_desc(self) -> str:
        return 'InfiniteFog'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        page = 1
        while page < 6:

            url = f'https://infinitefog.ru/shop/new'
            params = {
                'lang': 'en',
                'page': page
            }

            r = requests.get(url, params=params)
            soup = BeautifulSoup(r.text, features='html.parser')

            items = soup.select('article.goods-item')
            for item in items:

                auction_id = item.select_one('input[name="id"]')['value']
                title = item.select_one('h4.item-title').text.strip()
                link = 'https://infinitefog.ru/' + item.select_one('a')['href']
                image_link = 'https://infinitefog.ru' + item.select_one('img')['src'].replace('185x185/', '')
                _price = item.select_one('div.item-price').text.strip()
                _desc = item.select_one('div.goods-item_desc>p').text.strip()
                description = f"{_price}\n\n{_desc}"

                if self.search_term.lower() in title.lower():
                    auctions.append(
                        Auction(auction_id=auction_id,
                                description=description,
                                image_link=image_link,
                                link=link,
                                title=title,
                                start_date=datetime.now()
                                )
                    )

            page += 1

        return auctions
