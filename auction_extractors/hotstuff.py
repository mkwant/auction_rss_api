from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class HotStuff(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://hotstuff.se/index.cfm?x=product&pg=1&prSts=0&zpgId=&searchPhrase={self.search_term}&ordBy=add&view="

    @property
    def site_desc(self) -> str:
        return "HotStuff"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://hotstuff.se/index.cfm'
        params = {
            'x': 'product',
            'pg': 1,
            'prSts': 1,
            'searchPhrase': self.search_term,
            'ordBy': 'add',
        }

        r = httpx.get(url=url, params=params)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('div.xProductList>div')
        for item in items:
            title = item.select_one('a')['title']
            link = item.select_one('a')['href']
            auction_id = link.split('/')[-1]

            try:
                image_link = item.select_one('div[style^=background-image]')['style'].split('(')[1].split(')')[0]
            except TypeError:
                image_link = item.select_one('div.lazy')['data-original']

            description = item.select_one("div > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)").text

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
