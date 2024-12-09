import json
from typing import List

import dateparser
import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Tilburg013(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.013.nl/programma'

    @property
    def site_desc(self) -> str:
        return '013'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = requests.get(self.search_link)
        soup = BeautifulSoup(r.content, features='html.parser')
        items = soup.select('a.inline-flex')
        for item in items:
            _title = item.select_one('h2.text-lg').text.strip()

            try:
                _subtitle = item.select_one('h3.leading-relaxed').text.strip()
            except AttributeError:
                _subtitle = ''

            try:
                _flash = item.select_one('div.ribbon_basic').text.strip()
            except AttributeError:
                _flash = None

            try:
                desc = item.select_one('p.leading-snug').text.strip()
            except AttributeError:
                desc = ''
            link = item['href']
            event_id = link.split('/')[-2]

            image_link = \
                json.loads(item['@mouseenter.debounce.150ms'].split('(')[1].split(')')[0].replace(', true', ''))[
                    'jpg_srcset'].split()[-2]

            event_date = dateparser.parse(item.select_one('time')['datetime'])

            if _flash:
                title = f'{event_date:%a %Y-%m-%d}: [{_flash}] {_title}'
            else:
                title = f'{event_date:%a %Y-%m-%d}: [{_title}]'

            description = f'{_subtitle}\n{desc}'.strip()

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': event_id,
                    'description': description,
                    'image_link': image_link,
                    'link': link,
                }))

        return auctions
