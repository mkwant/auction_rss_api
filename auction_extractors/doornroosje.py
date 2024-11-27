from typing import List

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
            _event_date = ' '.join(event.select_one('div.c-program__date').get_text(separator='').strip().split())
            _event_info = event.select('div.c-program__info')
            _event_location = [
                info for info in _event_info if
                "c-program__info--subtitle" not in info['class'] and
                "c-program__info--highlighted" not in info['class']
            ]

            if _event_location:
                _event_location_name = _event_location[0].text.strip()
                title = f'{_event_date} [{_event_location_name}]: {_event_name}'
            else:
                title = f'{_event_date}: {_event_name}'
            description = event.select_one('div.c-program__info--subtitle').text.strip()

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': str(hash(link)),
                    'description': description,
                    'link': link
                }))

        return auctions
