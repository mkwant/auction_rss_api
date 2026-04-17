from typing import List

import cloudscraper
import dateparser
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class TivoliVredenburg(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.tivolivredenburg.nl/agenda/?nieuw=1'

    @property
    def site_desc(self) -> str:
        return 'Tivoli Vredenburg'

    def get_auctions(self) -> List[Auction]:
        auctions = []
        params = {
            'nieuw': '1',
        }

        s = cloudscraper.create_scraper()
        r = s.get(url='https://www.tivolivredenburg.nl/agenda/', params=params)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.content, features='html.parser')

        events = soup.select('li.agenda-list-item')
        for event in events:
            link = event.select_one('a.link')['href']
            try:
                image_link = event.select_one('img')['src']
            except TypeError:
                image_link = None
            event_id = link.split('/')[-2]

            _event_name = event.select_one('.agenda-list-item__title').text.strip()
            _event_date = event.select_one('.agenda-list-item__time').text.strip()
            _event_date = dateparser.parse(_event_date)
            title = f'{_event_date:%a %Y-%m-%d}: {_event_name}'

            try:
                description = event.select_one('.agenda-list-item__text').text.strip()
            except AttributeError:
                description = ''

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': event_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link
                }))

        return auctions
