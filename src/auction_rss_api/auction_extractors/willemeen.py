import hashlib
from datetime import datetime
from typing import List

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class WillemEen(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.willemeen.nl/programma/'

    @property
    def site_desc(self) -> str:
        return 'WillemEen'

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(self.search_link)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features='html.parser')

        auctions = []

        for row in soup.select(".we__agenda-row"):
            date_str = row.select_one(".we__agenda-item-date").text.strip()
            _date = dateparser.parse(date_str)
            if _date is not None:
                if _date.date() < datetime.today().date():
                    _date = _date.replace(year=_date.year + 1)

            for event in row.select(".we__agenda-item.concertfilterwebsite"):
                _title = event.select_one(".we__agenda-item-name > div[data-text]")["data-text"]

                title = f"{_date:%a %Y-%m-%d}: {_title}"
                link = str(event.select_one("a.stretched-link")["href"])
                unique_id = hashlib.md5(link.encode()).hexdigest()
                image_link = event["data-hover-image"].strip()
                _time = event.select_one(".we__agenda-item-info").text.strip()
                _genre = event.select_one(".we__agenda-item-genre").text.strip()
                description = f"{_time}\n{_genre}"

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
