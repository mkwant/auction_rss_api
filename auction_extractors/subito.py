import json
from datetime import datetime
from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Subito(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.subito.it/annunci-italia/vendita/sport-hobby/?q={self.search_term}&qso=true&o=1"

    @property
    def site_desc(self) -> str:
        return "Subito"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.subito.it/annunci-italia/vendita/sport-hobby/'
        params = {
            'q': self.search_term,
            'qso': True,
            'o': 1,
        }
        r = httpx.get(url=url, params=params)

        soup = BeautifulSoup(markup=r.text, features="html.parser")
        json_str = soup.select_one('script#__NEXT_DATA__').text
        json_parsed = json.loads(json_str)
        items = json_parsed['props']['pageProps']['initialState']['items']['list']
        for item in items:
            item = item['item']

            auction_id = item['urn'].split(':')[-1]
            title = item['subject']
            link = item['urls']['default']
            image_link = item['images'][0]['cdnBaseUrl'] + '?rule=gallery-desktop-1x-auto'
            date_published = datetime.fromisoformat(item['date'])
            _desc = item['body']
            _town = item['geo']['town']['value']
            _price = item['features']['/price']['values'][0]['value']

            try:
                _shipping = item['features']['/item_shipping_cost_tuttosubito']['values'][0]['value']
            except KeyError:
                _shipping = 'No shipping'
            description = f"Price: {_price}\nShipping: {_shipping}\nTown: {_town}\n\n{_desc}"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    description=description,
                    image_link=image_link,
                    start_date=date_published,
                )
            )

        return auctions
