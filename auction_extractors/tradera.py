import json
from typing import List, Literal

import dateutil
import requests
from bs4 import BeautifulSoup

from models.auctionextractor import AuctionExtractor
from models.auction import Auction


class Tradera(AuctionExtractor):
    search_term: str
    currency: Literal['DKK', 'EUR', 'GBP', 'JPY', 'NOK', 'SEK', 'USD'] = 'EUR'

    @property
    def search_link(self) -> str:
        return f'https://www.tradera.com/en/search?sortBy=AddedOn&q={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'Tradera'

    def _get_json_data(self) -> dict:
        """Find the json string on the page and parse it."""
        url = 'https://www.tradera.com/en/search'
        params = {
            'q': self.search_term,
            'sortBy': 'AddedOn'
        }
        cookies = {
            'preferred_currency': self.currency,
            'shipping_country': 'NL',
            'Srp_Item_Layout': 'layout-list'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'
        }

        r = requests.get(url=url, params=params, cookies=cookies, headers=headers)
        soup = BeautifulSoup(r.text, features='html.parser')

        json_str = soup.select_one(selector='script#__NEXT_DATA__', namespaces={'type': 'application/json'}).text
        return json.loads(json_str)['props']['pageProps']['initialState']

    def get_auctions(self) -> List[Auction]:
        data = self._get_json_data()
        currency = data['multiCurrency']['preferredCurrency']
        items = data['discover']['items']

        auctions = []

        for item in items:
            auction_id = str(item['itemId'])
            title = item['shortDescription']
            image_link = item['imageUrlTemplate'].replace('{format}', 'large-fit')
            link = item['itemUrl'].replace('tradera.com/', 'tradera.com/en/')
            start_date = dateutil.parser.isoparse(item['startDate'])
            seller = item['sellerAlias']

            # Add seller rating to seller if it exists
            try:
                _seller_rating = item['sellerDsrAverage']
                seller += f" ({_seller_rating:.1f})"
            except KeyError:
                pass

            # Build description from pricing info
            _price_auction = (f"{currency['symbolPrefix'] or currency['symbolSuffix']}"
                              f"{item['price'] * currency['rate']:.2f} ({item['totalBids']} bids, ending "
                              f"{dateutil.parser.isoparse(item['endDate']):%d-%m-%Y %H:%M})")
            _price_bin = (f"{currency['symbolPrefix'] or currency['symbolSuffix']}"
                          f"{item['buyNowPrice'] * currency['rate']:.2f} Buy It Now")
            _shipping_options = '\n'.join([(f"- {x['type']}: {currency['symbolPrefix'] or currency['symbolSuffix']}"
                                            f"{x['cost'] * currency['rate']:.2f}")
                                           for x in item['shippingOptions']])
            _price_shipping = f"\nShipping options:\n{_shipping_options}"

            type_desc_mapping = {
                'Auction': [_price_auction, _price_shipping],
                'AuctionBin': [_price_auction, _price_bin, _price_shipping],
                'PureBin': [_price_bin, _price_shipping],
                'ShopItem': [_price_bin, _price_shipping]
            }

            description = '\n'.join(type_desc_mapping.get(item['itemType'], []))

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                    seller=seller,
                    start_date=start_date
                )
            )
        return auctions
