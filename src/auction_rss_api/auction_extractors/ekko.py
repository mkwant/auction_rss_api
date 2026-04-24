from typing import List

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Ekko(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://ekko.nl/agenda/concert/"

    @property
    def site_desc(self) -> str:
        return "Ekko"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://ekko.nl/agenda/concert/'
        r = httpx.get(url=url)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features='html.parser')
        events = soup.select('div.pb-8>a')
        for event in events:
            link = str(event['href'])
            _event_name = event.select_one('h3').text
            _event_type = event['data-filter-value']
            if not 'concert' in _event_type.lower():
                continue
            try:
                _support = f"({event.select_one('span.text-small-mobile').text})"
            except AttributeError:
                _support = ''
            _date_str = ' '.join([x.strip() for x in event.select_one('span.whitespace-nowrap').get_text().split()])
            _date = dateparser.parse(_date_str)
            title = f"{_date:%a %Y-%m-%d} {_event_name} {_support}".strip()
            unique_id = f"{_date:%Y%m%d}-{link.split('/')[-2]}"

            try:
                description = event.select_one('div.marquee__inner>span').text.rstrip(' \xa0\xa0—\xa0\xa0')
            except AttributeError:
                description = ''

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    description=description,
                )
            )

        return auctions
