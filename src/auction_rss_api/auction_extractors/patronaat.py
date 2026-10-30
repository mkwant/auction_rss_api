import hashlib
from typing import List

import dateparser
import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Patronaat(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://patronaat.nl/programma/"

    @property
    def site_desc(self) -> str:
        return "Patronaat"

    def get_auctions(self) -> List[Auction]:
        r = httpx2.get(self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        auctions = []

        events = soup.select('div.overview__list-item--event')
        for event in events:
            _event_name = event.select_one('h3.event-program__name').text.strip()
            _event_date = dateparser.parse(event.select_one('div.event-program__date').text.strip())
            title = f"{_event_date:%a %Y-%m-%d}: {_event_name}"
            link = str(event.select_one('a')['href'])
            image_link = str(event.select_one('img')['src'])
            description = event.select_one('div.event-program__subtitle').text.strip()
            unique_id = hashlib.md5(link.encode('utf-8')).hexdigest()

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
