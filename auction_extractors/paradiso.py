from datetime import datetime
from typing import List

import dateparser
import requests

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Paradiso(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.paradiso.com/'

    @property
    def site_desc(self) -> str:
        return 'Paradiso'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        json_data = {
            'query': '\n  query programItemsQuery(\n    $site: String\n    $size: Int = 100\n    $gteStartDateTime: String\n    $lteStartDateTime: String\n    $searchAfter: [String]\n    $location: [Int]\n    $subBrand: [Int]\n    $contentCategory: [Int]\n    $highlight: Boolean = false\n  ) {\n    program(\n      site: $site\n      size: $size\n      gteStartDateTime: $gteStartDateTime\n      lteStartDateTime: $lteStartDateTime\n      searchAfter: $searchAfter\n      location: $location\n      subBrand: $subBrand\n      contentCategory: $contentCategory\n      highlight: $highlight\n    ) {\n      __typename\n      events {\n        __typename\n        id\n        uri\n        title\n        startDateTime\n        date\n        subtitle\n        sort\n        eventStatus\n        highlight\n        supportAct\n        announceSupport\n        soldOut\n        location {\n          id\n          title\n        }\n        image {\n          mobile\n          mobile2x\n          mobileWebp\n          mobile2xWebp\n          tablet\n          tablet2x\n          tabletWebp\n          tablet2xWebp\n          desktop\n          desktop2x\n          desktopWebp\n          desktop2xWebp\n          desktopL\n          desktopL2x\n          desktopLWebp\n          desktopL2xWebp\n          desktopXL\n          desktopXL2x\n          desktopXLWebp\n          desktopXL2xWebp\n          type\n        }\n      }\n    }\n  }\n',
            'variables': {
                'site': 'paradisoNederlands',
                'size': 382,  # Seems this is the maximum entries allowed
                'gteStartDateTime': f'{datetime.now():%Y-%m-%d}',
                'lteStartDateTime': None,
                'searchAfter': None,
                'location': None,
                'subBrand': None,
                'contentCategory': None,
            },
            'operationName': 'programItemsQuery',
        }

        r = requests.post(
            url='https://knwxh8dmh1.execute-api.eu-central-1.amazonaws.com/graphql',
            json=json_data
        )
        r.raise_for_status()
        print(r.status_code)
        print(r.json())
        events = r.json()['data']['program']['events']

        for event in events:
            auction_id = event['id']
            _event_title = event['title']
            _event_date = dateparser.parse(event['date'])
            _support = event['supportAct']
            _sold_out = event['soldOut']
            if not _sold_out == 'no':
                _sold_out_text = 'Sold Out'
            else:
                _sold_out_text = None

            _start_date = datetime.fromisoformat(event['startDateTime'])

            try:
                _location = event['location'][0]['title']
            except IndexError:
                _location = 'Afgelast'

            title = f'{_event_date:%a %Y-%m-%d} [{_location}]: {_event_title}'
            if _support:
                title += f' + {_support}'

            if event['eventStatus'] != 'confirmed' and event['eventStatus'] is not None:
                title = f"[{event['eventStatus'].upper()}] {title}"

            if _sold_out_text:
                title = f'[{_sold_out_text.upper()}] {title}'

            description = f'{event['subtitle']}\n{_start_date:%H:%M}'

            link = 'https://www.paradiso.nl/' + event['uri']
            image_link = event['image'][0]['desktopXL2x']

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'image_link': image_link,
                    'link': link,
                    'seller': _location
                }))

        return auctions
