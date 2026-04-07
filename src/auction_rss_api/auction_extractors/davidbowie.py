from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class DavidBowie(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://shop.davidbowie.com/collections/new-releases'

    @property
    def site_desc(self) -> str:
        return 'davidbowie.com'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = httpx.get(url=self.search_link)

        soup = BeautifulSoup(r.text, features='html.parser')
        items = soup.select('div.col-sm-6')
        for item in items:
            title = item.select_one('h4.product-card__title').text
            link = 'https://shop.davidbowie.com' + item.select_one('a')['href']
            auction_id = link.split('/')[-1]
            image_link = item.select_one('img')['src']
            desc = item.select_one('div.price').text.strip()

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=desc,
                    image_link=image_link,
                    link=link,
                    title=title,
                )
            )

        return auctions
