import hashlib
from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class BowieWebStore(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://bowiewebstore.com/store/'

    @property
    def site_desc(self) -> str:
        return 'BowieWebStore'

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(self.search_link)
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('div.product-card')

        auctions = []

        for item in items:
            title = item.select_one('div.product-card__title').text.strip()
            link = str(item.select_one('a')['href'])
            image_link = str(item.select_one('img')['src'])
            item_id = hashlib.md5(link.encode()).hexdigest()
            try:
                description = item.select_one('span.screen-reader-text').text.strip()
            except AttributeError:
                description = item.select_one('p.price').text.strip()

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
