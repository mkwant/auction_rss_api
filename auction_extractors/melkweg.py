from datetime import datetime
from typing import List

import requests
from dateutil import tz

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Melkweg(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.melkweg.nl/nl/agenda/'

    @property
    def site_desc(self) -> str:
        return 'Melkweg'

    def get_auctions(self) -> List[Auction]:
        auctions = []
        params = {
            'slug': [
                'nl',
                'agenda',
            ],
        }

        r = requests.get(
            url='https://www.melkweg.nl/_next/data/bfWrA95a0hXEiWpatMqbq/nl/agenda.json',
            params=params
        )

        timezone = tz.gettz('Europe/Amsterdam')

        events_1 = r.json()['pageProps']['pageData']['attributes']['content']
        events = events_1[0]['attributes']['initialEvents']
        for event in events:
            _event_type = event['attributes']['profile']
            if not _event_type in ['Concert', 'Festival']:
                continue

            event_id = event['id']
            _event_title = event['attributes']['name']
            _date_time = datetime.fromisoformat(event['attributes']['startDate']).astimezone(tz=timezone)
            _status = event['attributes']['status']

            title = f'{_date_time:%a %Y-%m-%d}: {_event_title}'

            if _status != 'Gepubliceerd':
                title = f'[{_status.upper()}] {title}'

            link = 'https://www.melkweg.nl' + event['attributes']['url']
            image_link = event['attributes']['media']['featuredImage'][0]['filename']
            description = ' | '.join(event['attributes']['tags'])
            created_date = datetime.fromisoformat(event['attributes']['createdAt']).astimezone(tz=timezone)

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': event_id,
                    'description': description,
                    'image_link': image_link,
                    'link': link,
                    'start_date': created_date,
                }))

        auctions.sort(key=lambda a: a.start_date, reverse=True)
        return auctions
