from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from models.auctionextractor import AuctionExtractor
from models.auction import Auction


class Tracks(AuctionExtractor):
    @property
    def site_desc(self) -> str:
        return 'Tracks.co.uk'

    @property
    def search_link(self) -> str:
        return f'https://www.tracks.co.uk/category/various-artists-memorabilia/{self.search_term}'

    search_term: str

    def _get_auctions(self) -> ResultSet:
        self.search_term = self.search_term.lower().replace(' ', '-')
        url = f"https://www.tracks.co.uk/category/various-artists-memorabilia/{self.search_term}"

        r = requests.get(url=url)
        soup = BeautifulSoup(r.content, features='html.parser')
        items = soup.select('ul.products li')
        return items

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in self._get_auctions():
            title = item.select_one('h2').get_text()
            _desc = item.select_one('div.woo-short-description').get_text(strip=True)
            image_link = item.select_one('img')['src']
            link = item.select_one('a.un-loop-thumbnail')['href']
            auction_id = link.split('/')[4].split('-')[0]
            _price = item.select_one('span.price').get_text()
            description = '\n'.join([_price, _desc])

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title
                )
            )

        return auctions
