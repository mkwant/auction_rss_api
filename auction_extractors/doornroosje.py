from typing import List

import dateparser
import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Doornroosje(AuctionExtractor):

    @property
    def search_link(self) -> str:
        return 'https://www.doornroosje.nl'

    @property
    def site_desc(self) -> str:
        return 'Doornroosje'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.doornroosje.nl/wp/wp-admin/admin-ajax.php'
        data = {
            'action': 'filter_taxonomy',
            'data[event-genre]': '',
            'data[event-location]': self.search_term,
            'data[month]': '',
            'data[hide-cancelled]': 'false',
            'data[confirmed-only]': 'true',
            'search': ''
        }
        r = requests.post(url=url, data=data)
        html = r.json()['program_html']
        soup = BeautifulSoup(html, features='html.parser')

        events = soup.select('a.c-program__item')
        for event in events:
            link = event['href']
            _event_name = event.select_one('span.c-program__title--main').text.strip()

            # Get event date and the year from a few levels up, parse and combine the two
            _event_date = ' '.join(event.select_one('div.c-program__date').get_text().strip().split())
            _event_year = dateparser.parse(event.parent.parent.select_one('h2.c-program__month').text).year
            _event_date = dateparser.parse(_event_date)
            _event_date = _event_date.replace(year=_event_year)
            _event_info = event.select('div.c-program__info')

            _event_location = [
                info for info in _event_info if
                "c-program__info--subtitle" not in info['class'] and
                "c-program__info--highlighted" not in info['class']
            ]

            if _event_location:
                _event_location_name = _event_location[0].text.strip()
                title = f'{_event_date:%a %Y-%m-%d} [{_event_location_name}]: {_event_name}'
            else:
                title = f'{_event_date:%a %Y-%m-%d}: {_event_name}'
            try:
                description = event.select_one('div.c-program__info--subtitle').text.strip()
            except AttributeError:
                description = ''

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': str(hash(link)),
                    'description': description,
                    'link': link
                }))

        return auctions
