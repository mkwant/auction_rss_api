import json
from datetime import datetime
from typing import List

import dateparser
import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Effenaar(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.effenaar.nl/agenda?state=new'

    @property
    def site_desc(self) -> str:
        return 'Effenaar'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = requests.get(self.search_link)

        soup = BeautifulSoup(r.content, features='html.parser')
        events = soup.select('a.agenda-card')
        for event in events:
            event_id = str(hash(event['href']))
            link = 'https://effenaar.nl' + event['href']
            image_link = event.select_one('img')['data-srcset'].split(',')[-1].split()[0]
            _title = event.select_one('h3.card-title').text.strip()
            _date = event.select_one('div.card-info-date').text.strip()
            _date = dateparser.parse(_date)
            _location = event.select_one('div.card-info-location').text.strip()
            title = f"{_date:%a %Y-%m-%d}: [{_location}] {_title}"
            description = event.select_one('p.card-subtitle').text.strip()

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': event_id,
                    'description': description,
                    'image_link': image_link,
                    'link': link,
                }))

        return auctions
