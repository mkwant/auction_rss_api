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
            json_data['requests'][0]['params']['facetFilters'] = ['attributes.exclusive:Rough Trade Exclusive']

        r = httpx.post(
            url='https://www.roughtrade.com/api/algolia/search',
            headers=headers,
            json=json_data
        )

        auctions = []
        items = r.json()['results'][0]['hits']
        for item in items:
            unique_id = str(item['variant']['id'])

            _artist = item['product']['artist_primary']
            _title = item['product']['title']
            _variant = item['variant']['title']
            title = f"{_artist} - {_title} ({_variant})"

            try:
                # link = f'https://www.roughtrade.com/en-de/product/{item['artists'][0]['handle']}/{item['product']['handle']}'
                link = f'https://www.roughtrade.com/en-de/product/{item['product']['artist_primary']}/{item['product']['handle']}'
            except IndexError:
                link = f'https://www.roughtrade.com/en-de/product/{item['product']['product_type'].lower().replace(' ', '-')}/{item['product']['handle']}'

            image_link = item['variant']['image']

            created_at = item['product']['published_at']

            try:
                _price = f"Eur {item['market_pricing']['eur']['price']}"
            except KeyError:
                continue
            if item['is_pre_order']:
                _price = f"PREORDER ({item['availability']['release_date']}): {_price}"

            if not item['availability']['inventory_available']:
                _price = f"SOLD OUT: {_price}"

            _desc = item['product']['description_text'].strip()

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
