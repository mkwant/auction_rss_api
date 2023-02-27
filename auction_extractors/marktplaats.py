import re

import requests
from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class Marktplaats(AuctionExtractor):
    search_term: str
    search_in_seller_name: bool = False
    CURRENT_PAGE = 0
    LIMIT = 100
    DOMAIN = 'marktplaats.nl'
    SITE_DESC = 'Marktplaats'

    @staticmethod
    def clean_control_chars(string: str) -> str:
        """Removes certain control characters."""
        return re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', string)

    def search(self, ) -> AuctionSearchResponse:
        params = {
            'limit': self.LIMIT,
            'offset': self.CURRENT_PAGE,
            'postcode': '',
            'query': self.search_term,
            'searchInTitleAndDescription': 'false',
            'sortBy': 'SORT_INDEX',
            'sortOrder': 'DECREASING',
            'viewOptions': 'list-view'
        }

        api_endpoint = f'https://www.{self.DOMAIN}/lrp/api/search'
        r = requests.get(api_endpoint, params=params)
        mp_items = r.json()['listings']

        auctions = []

        for item in mp_items:
            if not self.search_in_seller_name:
                if self.search_term.lower() in item['sellerInformation']['sellerName'].lower() \
                        and self.search_term not in item['title']:
                    continue

            try:
                image_link = item['pictures'][0]['extraExtraLargeUrl']
            except KeyError:
                image_link = None

            auction = {'auction_id': item['itemId'],
                       'description': f"{item['priceInfo']['priceType']}: "
                                      f"{item['priceInfo']['priceCents'] / 100:.2f}\n"
                                      f"{self.clean_control_chars(item['description'])}",
                       'link': f"https://www.{self.DOMAIN}{item['vipUrl']}",
                       'image_link': image_link,
                       'title': self.clean_control_chars(item['title']),
                       'seller': item['sellerInformation']['sellerName'],
                       'start_date': item['date']}

            auctions.append(Auction(**auction))

        return AuctionSearchResponse(
            search_link=f'https://www.{self.DOMAIN}/q/{self.search_term}',
            search_term=self.search_term,
            site_desc=f'{self.SITE_DESC}',
            auctions=auctions
        )
