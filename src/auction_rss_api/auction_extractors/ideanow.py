from typing import List

import httpx

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class IdeaNow(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.ideanow.online/store/search?keyword={self.search_term}&sort=addedTimeDesc&limit=100'

    @property
    def site_desc(self) -> str:
        return 'IdeaNow'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        payload = {
            'productFiltersValue': {
                'keyword': self.search_term,
            },
            'sortBy': 'addedTimeDesc',
            'pagination': {
                'offset': 0,
                'limit': 100,
            },
            'urlParams': {
                'baseUrl': '/store',
                'canonicalBaseUrl': '',
                'isCleanUrls': True,
                'isCanonicalUrlsEnabled': True,
                'isSlugsWithoutIds': False,
            },
            'lang': 'en',
        }

        r = httpx.post(url='https://app.ecwid.com/storefront/api/v1/7909113/catalog/search', json=payload)
        for product in r.json()['products']:
            auction_id = str(product['identifier']['productId'])
            title = product['name']
            link = 'https://www.ideanow.online' + product['urls']['shareUrl']
            image_link = product['defaultOptionsOverrides']['variationOverrides']['mediaItems'][0]['imageOriginalUrl']
            _price = product['defaultOptionsOverrides']['pricesOverrides']['basePriceWithModifiersDiscount']
            _desc = product['description']
            desc = f'£{_price:.2f}\n\n{_desc}'

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=desc,
                )
            )

        return auctions
