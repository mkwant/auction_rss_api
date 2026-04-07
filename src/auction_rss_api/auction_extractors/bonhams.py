import datetime
import json
from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Bonhams(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.bonhams.com/search/?chronology=future&query={self.search_term}&sortBy=lots_virtual_sort_hammertime_desc'

    @property
    def site_desc(self) -> str:
        return "Bonhams"

    @staticmethod
    def ts_to_date(timestamp: str) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(timestamp=float(timestamp), tz=datetime.timezone.utc)

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.bonhams.com/search/'
        params = {
            'chronology': 'future',
            'query': self.search_term,
            'sortBy': 'lots_virtual_sort_hammertime_desc',
        }
        r = httpx.get(url=url, params=params)
        soup = BeautifulSoup(r.text, features="html.parser")
        json_str = soup.select_one('script[type="application/json"]').text.strip()
        json_parsed = json.loads(json_str)
        items = json_parsed['props']['pageProps']['lotData']['pagesOfLots'][0]

        for item in items:
            auction_id = item['id']
            title = item['image']['caption']
            if title == "":
                title = item['title']

            link = f'https://www.bonhams.com/auction/{item['auctionId']}/lot/{item['lotId']}/{item['slug']}'
            image_link = item['image']['url']
            _price = f"{item['price']['currencySymbol']}{item['price']['estimateLow']}-{item['price']['estimateHigh']}"
            _hammertime = f"{self.ts_to_date(item['hammerTime']['timestamp']):%Y-%m-%d %H:%M}"
            description = f"{item['heading']}\n{item['title']}\n\nEstimate: {_price}\n\nHammer time: {_hammertime}"
            try:
                _bidding_start = f"{self.ts_to_date(item['biddableFrom']['timestamp']):%Y-%m-%d %H:%M}"
                description += f'\nBidding start: {_bidding_start}'
            except KeyError:
                pass

            creation_date = self.ts_to_date(item['updatedAt']['timestamp'])

            auctions.append(
                Auction(auction_id=auction_id,
                        description=description,
                        image_link=image_link,
                        link=link,
                        title=title,
                        start_date=creation_date,
                        )
            )

        return auctions
