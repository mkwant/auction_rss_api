from datetime import datetime
from typing import List

import httpx

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class RoughTrade(AuctionExtractor):
    available_only: bool = False
    exclusives_only: bool = False

    @property
    def search_link(self) -> str:
        return f"https://www.roughtrade.com/en-de/search?q={self.search_term}&sortBy=newest_listed"

    @property
    def site_desc(self) -> str:
        return "RoughTrade"

    def get_auctions(self) -> List[Auction]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0'}

        if self.search_term is None:
            self.search_term = ''

        json_data = {
            'requests': [
                {
                    'indexName': 'shopify_prod_products_newest_listed',
                    'params': {
                        'facetFilters': [],
                        'hitsPerPage': 80,
                        'page': 0,
                        'query': self.search_term,
                    },
                }
            ],
        }

        if self.exclusives_only:
            json_data['requests'][0]['params']['facetFilters'] = ['meta.custom.exclusive:Rough Trade Exclusive']

        r = httpx.post(
            url='https://www.roughtrade.com/api/algolia/search',
            headers=headers,
            json=json_data
        )

        auctions = []
        items = r.json()['results'][0]['hits']
        for item in items:
            unique_id = str(item['id'])
            title = f"{item['product_type']} - {item['title']} ({item['option1']})"

            try:
                link = f'https://www.roughtrade.com/en-de/product/{item['artists'][0]['handle']}/{item['handle']}'
            except IndexError:
                link = f'https://www.roughtrade.com/en-de/product/{item['product_type'].lower().replace(' ', '-')}/{item['handle']}'
            image_link = item['image']
            created_at = datetime.fromisoformat(item['created_at'])

            _price = f"Eur {item['market_pricing']['eur']['price']}"
            if item['is_pre_order']:
                _price = f"PREORDER ({item['meta']['custom']['release_date']}): {_price}"

            if not item['inventory_available']:
                _price = f"SOLD OUT: {_price}"

                # Skip if available_only is set and item is not available
                if self.available_only:
                    continue

            _desc = item['body_html_safe'].strip()

            description = f"{_price}\n\n{_desc}"

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                    start_date=created_at,
                )
            )

        return auctions
