import hashlib
from datetime import datetime
from typing import List
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class IllustratedDBDiscography(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://www.illustrated-db-discography.nl/History.htm"

    @property
    def site_desc(self) -> str:
        return "IllustratedDBDiscography"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url=self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features="html.parser")

        items = soup.select("div.topbottom > p")

        auctions = []

        for item in items:
            full_html = item.decode_contents()

            try:
                version_and_date, body_html = full_html.split(sep=":", maxsplit=1)
            except ValueError:
                # Skip items without a colon
                continue

            version = version_and_date.split("(")[0].strip()
            unique_id = hashlib.md5(version.encode('utf-8')).hexdigest()
            date = datetime.strptime(version_and_date.split("(")[1].split(")")[0].strip(), '%d-%m-%y')

            # Make all links absolute
            item_soup = BeautifulSoup(markup=body_html, features="html.parser")
            for a in item_soup.select("a[href]"):
                a["href"] = urljoin(base=self.search_link, url=str(a["href"]))
            description = str(item_soup).strip()

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=version,
                    link=self.search_link,
                    description=description,
                    start_date=date,
                )
            )

        return auctions
