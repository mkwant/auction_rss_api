import json
from datetime import datetime
from typing import List

import cloudscraper
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Subito(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.subito.it/annunci-italia/vendita/sport-hobby/?q={self.search_term}&qso=true&o=1"

    @property
    def site_desc(self) -> str:
        return "Subito"

    def get_auctions(self) -> List[Auction]:
        auctions = []
        scraper = cloudscraper.create_scraper()

        url = 'https://www.subito.it/annunci-italia/vendita/sport-hobby/'
        params = {
            'q': self.search_term,
            'qso': True,
            'o': 1,
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0'}
        r = scraper.get(url=url, params=params, headers=headers)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features="html.parser")
        json_str = soup.select_one('script#__NEXT_DATA__').text
        json_parsed = json.loads(json_str)
        items = json_parsed['props']['pageProps']['initialState']['items']['originalList']
        for item in items:
            auction_id = item['urn'].split(':')[-1]
            title = item['subject']
            link = item['urls']['default']
            image_link = item['images'][0]['cdnBaseUrl'] + '?rule=gallery-desktop-1x-auto'
            date_published = datetime.fromisoformat(item['date'])
            _desc = item['body']
            _town = item['geo']['town']['value']

            try:
                _price = item['features']['/price']['values'][0]['value']
            except KeyError:
                _price = 'No price'

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
