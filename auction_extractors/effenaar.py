import json
from datetime import datetime
from typing import List

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

        params = {
            'state': 'new',
        }

        r = requests.get(url='https://www.effenaar.nl/agenda', params=params)
        soup = BeautifulSoup(r.content, features='html.parser')

        json_str = soup.select_one('script#__NEXT_DATA__').text
        queries = json.loads(json_str)['props']['pageProps']['dehydrated']['queries']
        events = \
            queries[8]['state']['data']['pageData']['algolia']['serverState']['initialResults']['production_events'][
                'results'][0]['hits']
        for event in events:
            event_id = event['objectID'].split('/')[1].split(':')[0]

            _date = datetime.fromtimestamp(event['date']).date()
            _location = event['locations'][0]['title']
            _title = event['title']
            title = f'{_date}: [{_location}] {_title}'
            link = 'https://www.effenaar.nl' + event['slug']
            image_link = event['thumbnail_image']['image']['sizes']['2510s']

            publish_date = datetime.fromtimestamp(event['publish_date'])

            _subtitle = event['subtitle']
            _introduction = event['introduction'].strip()

            description = f'{_subtitle}\n\n{_introduction}'

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': event_id,
                    'description': description,
                    'image_link': image_link,
                    'link': link,
                    'start_date': publish_date,
                }))

            auctions.sort(key=lambda a: a.start_date, reverse=True)

        return auctions
