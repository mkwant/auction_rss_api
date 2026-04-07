from datetime import datetime
from typing import List
from urllib.parse import parse_qs, urlparse

import dateparser
import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Vera(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.vera-groningen.nl/programma/'

    @property
    def site_desc(self) -> str:
        return 'Vera'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.vera-groningen.nl/wp/wp-admin/admin-ajax.php'
        params = {
            'action': 'renderProgramme',
            'category': 'all',
            'page': 1,
            'perpage': 100
        }
        r = requests.get(url=url, params=params)
        soup = BeautifulSoup(r.content, features='html.parser')
        events = soup.select('div.event-wrapper')
        for event in events:

            # Artist origin country is in subscript, add brackets and spaces around it
            artist = event.select_one('h3.artist')
            origins = artist.find_all('sup')
            for origin in origins:
                if origin.text:
                    origin.replace_with(soup.new_string(f' ({origin.text.strip()}) '))

            _title = event.select_one('h3.artist').text.strip()

            try:
                _subtitle = event.select_one('h4.pretitle').text.strip()
            except AttributeError:
                _subtitle = None

            _event_date = event.select_one('div.date')
            try:
                _event_date.span.decompose()
            except AttributeError:
                pass
            _event_date = dateparser.parse(_event_date.text.strip())
            if _event_date < datetime.now():
                _event_date = _event_date.replace(year=_event_date.year + 1)

            link = event.select_one('a.event-link')['href']
            image_link = event.select_one('div.artist-image')['style'].split('\'')[-2].replace('-360x250', '')
            description = event.select_one('div.schedule').text.strip()
            title = f'{_event_date:%a %Y-%m-%d}: {_title}'

            # Extracting support act, replacing sup_tag by brackets
            try:
                _support = event.select_one('h4.extra')
                origins = _support.find_all('sup')
                for origin in origins:
                    if origin.text:
                        origin.replace_with(soup.new_string(f' ({origin.text.strip()}) '))
            except AttributeError:
                _support = None

            if _support:
                _support = ' '.join([x.strip() for x in _support.get_text().split('\n') if x])
                title += f' | {_support}'

            if _subtitle:
                description = f'{_subtitle}\n\n{description}'

            event_id = parse_qs(urlparse(link).query)['p'][0]
            print(title)

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': event_id,
                    'description': description,
                    'image_link': image_link,
                    'link': link,
                }))

        return auctions
