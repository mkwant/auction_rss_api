from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class MusicHug(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.musikhug.ch/de/search/Section1.htm?query={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "MusikHug"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.musikhug.ch/de/search/Section1.htm'
        params = {'query': self.search_term}

        r = httpx.get(url=url, params=params)
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('article.article-list-item')
        for item in items:
            item_id = item.select_one('button.opc-favorite-button')["data-op-artno"]
            title = item.select_one('span.list-view').text.strip()
            link = 'https://www.musikhug.ch' + item.select_one('a')["href"]
            image_link = 'https://www.musikhug.ch' + item.select_one('img')['src'].replace('_M_', '_L_')
            description = item.select_one('span.price-basis').text.strip()

            auctions.append(
                Auction(
                    auction_id=item_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
