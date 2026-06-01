import hashlib
from datetime import datetime
from typing import List
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class JustAnotherCollection(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "http://bowie-collection.de/update_history.htm"  # noqa

    @property
    def site_desc(self) -> str:
        return "JustAnotherCollection"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url=self.search_link)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features="html.parser")

        table = soup.select("table")[1]

        for a in table.find_all(name="a", href=True):
            a["href"] = urljoin(base=self.search_link, url=str(a["href"]))

        auctions = []

        items = table.select("tr")
        for item in items:
            date_str = item.select("td")[1].text.strip()
            unique_id = hashlib.md5(date_str.encode()).hexdigest()
            description = item.select("td")[2].decode_contents()

            try:
                updated = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                # Skip rows without a date
                continue

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=date_str,
                    link=self.search_link,
                    description=description,
                    start_date=updated,
                )
            )

        return auctions
