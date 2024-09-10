from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from models.auctionextractor import AuctionExtractor
from models.auction import Auction


class KontaktAudio(AuctionExtractor):
    search_term: str

    @property
    def site_desc(self) -> str:
        return 'KontaktAudio'

    @property
    def search_link(self) -> str:
        return f'https://www.kontaktaudio.com'

    def _get_auctions(self) -> ResultSet:
        r = requests.get(url=self.search_link)
        soup = BeautifulSoup(r.text, features='html.parser')

        return soup.select('li.product')

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in self._get_auctions():
            item_id = item.select_one('div.quickview')['data-id']
            link = item.select_one('a')['href']
            image_link = item.select_one('img')['src'].replace('-300x300', '')
            title = item.select_one('h3.woocommerce-loop-product__title').get_text(strip=True)
            description = item.select_one('span.amount').get_text(strip=True)

            if self.search_term.lower() not in title.lower():
                continue

            auctions.append(
                Auction(
                    auction_id=item_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title
                )
            )

        return auctions
