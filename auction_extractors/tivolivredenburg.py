from typing import List

import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


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

        r = requests.get(url='https://www.tivolivredenburg.nl/agenda/', params=params)
        soup = BeautifulSoup(r.content, features='html.parser')

        events = soup.select('li.agenda-list-item')
        for event in events:
            link = event.select_one('a.link')['href']
            image_link = event.select_one('img')['src']
            event_id = link.split('/')[-2]

            _event_name = event.select_one('.agenda-list-item__title').text.strip()
            _event_date = event.select_one('.agenda-list-item__time').text.strip()
            title = f'{_event_date}: {_event_name}'
            description = event.select_one('.agenda-list-item__text').text.strip()

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': event_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link
                }))

        return auctions
