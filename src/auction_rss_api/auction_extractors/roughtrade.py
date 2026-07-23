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
        if self.exclusives_only:
            base_url = 'https://www.roughtrade.com/en-de/collection/exclusive'
        else:
            base_url = 'https://www.roughtrade.com/en-de/search'
        url =  f"{base_url}?sortBy=newest_listed"
        if self.search_term is not None:
            url = f"{url}&q={self.search_term}"
        return url

    @property
    def site_desc(self) -> str:
        return "RoughTrade"

    def get_auctions(self) -> List[Auction]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0'}

        # Quote search terms to disable fuzzy search
        search_term = ' '.join([f"\"{x}\"" for x in self.search_term.split()] if self.search_term else [''])

        json_data = {
            'requests': [
                {
                    'indexName': 'shopify_prod_products_newest_listed',
                    'params': {
                        'facetFilters': [],
                        'hitsPerPage': 80,
                        'page': 0,
                        'query': search_term,
                        'filters': 'markets.european_union.available:true',
                    },
                }
            ],
        }

        if self.exclusives_only:
            json_data['requests'][0]['params']['facetFilters'] = ['attributes.exclusive:Rough Trade Exclusive']

        r = httpx.post(
            url='https://www.roughtrade.com/api/algolia/search',
            headers=headers,
            json=json_data,
            timeout=10.0,
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
                link = f'https://www.roughtrade.com/en-de/product/{item['taxonomy']['artists'][0]['handle']}/{item['product']['handle']}'
            except IndexError:
                link = f'https://www.roughtrade.com/en-de/product/music/{item['product']['handle']}'
            image_link = item['variant']['image']

            created_at = item['product']['published_at']

            try:
                _price = f"Eur {item['markets']['european_union']['price']}"
            except KeyError:
                continue

            is_pre_order = any(c["label"] == "Pre-Orders" for c in item['taxonomy']['collections'])

            if is_pre_order:
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
