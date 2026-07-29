from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class ObscuurRecords(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://obscuurrecords.nl/index.php?route=product/search&search={self.search_term}&description=true'

    @property
    def site_desc(self) -> str:
        return "ObscuurRecords"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(self.search_link)
        r.raise_for_status()

        auctions = []

        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select("div.s_item")
        for item in items:
            unique_id = item["class"][-1]
            title = item.select_one("h3>a").text.strip()
            link = str(item.select_one("h3>a")["href"])
            image_link = str(item.select_one("img")["src"])
            description = ''.join(item.select_one("span.s_price").stripped_strings)

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
