from typing import List

import httpx2

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class VinylmaniaExtractor(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://vinylmania.net/?swp_form%5Bform_id%5D=1&s={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'VinylMania'

    def get_auctions(self) -> List[Auction]:

        auctions = []

        url = f'https://vinylmania.net/wp-json/wc/store/v1/products?search={self.search_term}&orderby=date&order=desc&per_page=100&page=1'

        r = httpx2.get(url=url)
        r.raise_for_status()

        items = r.json()
        for item in items:
            unique_id = item['slug']
            _title = item['name']
            _country = item['tags'][0]['name']
            _category = item['categories'][1]['name']
            title = f'{_title} | {_country} | {_category}'

            link = item['permalink']
            image_link = item['images'][0]['src']

            _price = int(item['prices']['price'])
            if _price == 0:
                _price = 'Offer'
            else:
                _price = f"€{_price / 100:.2f}"

            _desc = item['description']

            description = f"{_price}\n\n{_desc}"

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
