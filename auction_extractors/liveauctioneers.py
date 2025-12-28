import json
from datetime import datetime
from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class LiveAuctioneers(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.liveauctioneers.com/search/?keyword={self.search_term}&pageSize=48&sort=-publishDate&status=online'

    @property
    def site_desc(self) -> str:
        return "LiveAuctioneers"

    def get_auctions(self) -> List[Auction]:
        url = 'https://www.liveauctioneers.com/search/'
        params = {'keyword': self.search_term, 'sort': '-publishDate', 'status': 'online', 'pageSize': 48}

        r = httpx.get(url=url, params=params)

        soup = BeautifulSoup(markup=r.text, features='html.parser')
        script = soup.select_one('script:not([async]):not([id]):not([type]):not([defer])')
        json_str = \
            script.text.lstrip('window.__data=').replace('undefined', 'null').split(';window.__amplitude')[0]

        json_parsed = json.loads(json_str)
        items = json_parsed['itemSummary']['byId']

        auctions = []

        for auction_id in items:
            item = items[auction_id]
            link = f'https://www.liveauctioneers.com/item/{auction_id}_{item["slugWithLocation"]}'
            image_link = f'https://p1.liveauctioneers.com/{item['sellerId']}/{item['catalogId']}/{auction_id}_1_x.jpg'
            title = item['title']
            _catalog = item['catalogTitle']
            _currency = item['currency']
            _low_bid_estimate = item['lowBidEstimate']
            _high_bid_estimate = item['highBidEstimate']
            _start_price = item['startPrice']
            _desc = item['shortDescription']
            _start_time = datetime.fromtimestamp(item['saleStartTs'])

            description = (f"Start time: {_start_time}\nEstimate: {_currency} {_low_bid_estimate}-{_high_bid_estimate}"
                           f"\nStart bid: {_currency} {_start_price}\n\n{_desc}\n\n{_catalog}")

            seller = item['sellerName']

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title,
                    seller=seller
                )
            )

        auctions = sorted(auctions, key=lambda auction: auction.auction_id, reverse=True)
        return auctions
