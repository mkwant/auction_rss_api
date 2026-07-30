import hashlib
from typing import List

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Skeletunes(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://skeletunes.net/?s={self.search_term}&post_type=product'

    @property
    def site_desc(self) -> str:
        return "Skeletunes"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url=self.search_link)
        r.raise_for_status()

        auctions = []

        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('div.fl-post-grid-post')
        for item in items:
            title = str(item.select_one('meta[itemprop="mainEntityOfPage"]')['content'])
            link = str(item.select_one('meta[itemprop="mainEntityOfPage"]')['itemid'])
            unique_id = hashlib.md5(link.encode('utf-8')).hexdigest()
            image_link = str(item.select_one('div[itemprop="image"]>meta[itemprop="url"]')['content'])
            date_published = dateparser.parse(str(item.select_one('meta[itemprop="datePublished"]')['content']))

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description='',
                    start_date=date_published,
                )
            )
        return auctions
