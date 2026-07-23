import datetime
import hashlib
from datetime import date
from typing import List

import dateparser
import requests
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


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
            'data[confirmed-only]': 'false',
            'search': ''
        }

        r = requests.post(url=url, data=data)
        html = r.json()['program_html']
        soup = BeautifulSoup(html, features='html.parser')

        # Iterate over each month separately
        for program in soup.select('div.c-program'):
            month_text = program.select_one('h2.c-program__month').text.strip()

            try:
                event_year = dateparser.parse(month_text).year
            except AttributeError:
                event_year = datetime.datetime.now().year

            current_date = None

            for event in program.select('a.c-program__item'):
                link = event['href']
                event_name = event.select_one('span.c-program__title--main').text.strip()

                # Same-date events have an empty date div, so reuse the previous one
                date_text = ' '.join(event.select_one('div.c-program__date').stripped_strings)
                if date_text:
                    parsed = dateparser.parse(date_text)
                    if parsed is not None:
                        current_date = parsed.replace(year=event_year)

                # Should never happen, but keep a fallback
                if current_date is None:
                    current_date = date(year=event_year, month=1, day=1)

                event_info = event.select('div.c-program__info')

                event_location = [
                    info for info in event_info
                    if "c-program__info--subtitle" not in info.get('class', [])
                    and "c-program__info--highlighted" not in info.get('class', [])
                ]

                if event_location:
                    event_location_name = event_location[0].text.strip()
                    title = f'{current_date:%a %Y-%m-%d} [{event_location_name}]: {event_name}'
                else:
                    title = f'{current_date:%a %Y-%m-%d}: {event_name}'

                try:
                    description = event.select_one('div.c-program__info--subtitle').text.strip()
                except AttributeError:
                    description = ''

                auction_id = hashlib.md5(link.encode('utf-8')).hexdigest()

                auctions.append(
                    Auction(
                        title=title,
                        auction_id=auction_id,
                        description=description,
                        link=str(link),
                    )
                )

        return auctions