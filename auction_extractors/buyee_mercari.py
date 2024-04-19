import json
from datetime import datetime
from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auctionextractor import AuctionExtractor
from models.auction import Auction


class BuyeeMercari(AuctionExtractor):
    search_term: str

    @property
    def site_desc(self) -> str:
        return 'Buyee (Mercari)'

    @property
    def search_link(self) -> str:
        return (f'https://buyee.jp/mercari/search?keyword={self.search_term}'
                f'&status=all&items=40&lang=en&currencyCode=EUR')

    def _get_page(self) -> str:
        """Retrieve search page."""
        url = 'https://asf.myeeglobal.com/mercari'
        params = {'keyword': self.search_term,
                  'status': 'all',
                  'conversionType': 'Mercari_DirectSearch',
                  'currencyCode': 'EUR',
                  'myee': 0,
                  'languageCode': 'en',
                  'lang': 'en'
                  }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'
        }
        client = httpx.Client(headers=headers)
        r = client.get(url=url, params=params)
        r.raise_for_status()
        return r.text

    def get_auctions(self) -> List[Auction]:
        """Parse search page."""
        soup = BeautifulSoup(self._get_page(), features='html.parser')
        json_string = soup.select_one('script#__NEXT_DATA__').contents[0]
        parsed_json = json.loads(str(json_string))
        auction_list = parsed_json['props']['pageProps']['catalog']['entries']
        auctions = []

        for auction in auction_list:
            title = auction['names']['ja']
            auction_id = auction['item']['code']
            link = f"https://buyee.jp/mercari/item/{auction_id}"
            image_link = f"https://static.mercdn.net/item/detail/orig/photos/{auction_id}_1.jpg"
            _price_yen = f"{auction['price']['value']:,} yen"
            _price_eur = f"€{auction['localPrice']['value']:.2f}"
            if not auction['hasStock']:
                description = f'SOLD - {_price_yen} ({_price_eur})'
            else:
                description = f'{_price_yen} ({_price_eur})'
            seller = auction['store']['names']['ja']

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link,
                    'seller': seller,
                    'start_date': datetime.now()
                }))
        return auctions
