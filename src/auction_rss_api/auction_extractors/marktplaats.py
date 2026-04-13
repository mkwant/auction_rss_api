import re
from typing import List

import dateparser
import requests

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Marktplaats(AuctionExtractor):
    search_term: str
    search_in_seller_name: bool = False
    disable_fuzzy_search: bool = True
    CURRENT_PAGE: int = 0
    LIMIT: int = 100
    DOMAIN: str = 'marktplaats.nl'

    @property
    def site_desc(self) -> str:
        return 'Marktplaats'

    @property
    def search_link(self) -> str:
        return f'https://www.{self.DOMAIN}/q/{self.search_term}'

    @staticmethod
    def clean_control_chars(string: str) -> str:
        """Removes certain control characters."""
        return re.sub(
            pattern=u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+',
            repl='',
            string=string
        )

    def get_auctions(self) -> List[Auction]:
        params = {
            'limit': self.LIMIT,
            'offset': self.CURRENT_PAGE,
            'postcode': '',
            'query': self.search_term,
            'searchInTitleAndDescription': 'false',
            'bypassSpellingSuggestion': str(self.disable_fuzzy_search).lower(),
            'sortBy': 'SORT_INDEX',
            'sortOrder': 'DECREASING',
            'viewOptions': 'list-view'
        }

        api_endpoint = f'https://www.{self.DOMAIN}/lrp/api/search'
        r = requests.get(api_endpoint, params=params)
        mp_items = r.json()['listings']

        auctions = []

        for item in mp_items:
            # Skip sponsored items
            if item['searchType'] == 'kNN':
                continue

            if not self.search_in_seller_name:
                if self.search_term.lower() in item['sellerInformation']['sellerName'].lower() \
                        and self.search_term not in item['title']:
                    continue

            try:
                image_link = item['pictures'][0]['extraExtraLargeUrl']
            except KeyError:
                image_link = None

            auction = {
                'auction_id': item['itemId'],
                'description': f"{item['priceInfo']['priceType']}: "
                               f"{item['priceInfo']['priceCents'] / 100:.2f}\n"
                               f"{self.clean_control_chars(item['description'])}",
                'link': f"https://www.{self.DOMAIN}{item['vipUrl']}",
                'image_link': image_link,
                'title': self.clean_control_chars(item['title']),
                'seller': item['sellerInformation']['sellerName'],
                'start_date': dateparser.parse(date_string=item['date'], languages=['nl'])
            }

            auctions.append(
                Auction(**auction)
            )

        return auctions
