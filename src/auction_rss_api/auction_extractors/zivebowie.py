import hashlib
from typing import List

import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class ZiveBowieCollection(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://www.zivebowiecollection.com/whats-new/"

    @property
    def site_desc(self) -> str:
        return "Zive Bowie Collection"

    def get_auctions(self) -> List[Auction]:
        r = httpx2.get(url=self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')

        items = soup.select('div.elementor-container')

        auctions = []
        for item in items:
            title = item.select_one('h4.elementor-heading-title').text.strip()
            unique_id = hashlib.md5(title.encode()).hexdigest()
            description = " ".join(item.select_one('div.gallery').__str__().split())

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    description=description,
                    link=self.search_link,
                )
            )

        return auctions
