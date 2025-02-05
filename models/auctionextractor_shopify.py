import json
from abc import ABC, abstractmethod
from typing import List

import dateparser
import requests

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class ShopifyExtractor(AuctionExtractor, ABC):
    """A base class for Shopify sites."""
    search_in_desc: bool = False

    @property
    @abstractmethod
    def domain(self) -> str:
        """The domain of the Shopify site, i.e 'mysite.com'."""
        ...

    @property
    def search_link(self) -> str:
        return f"https://www.{self.domain}/search?q={self.search_term}"

    def get_auctions(self) -> List[Auction]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'
        }

        auctions = []

        url = f'https://www.{self.domain}/products.json?limit=250'
        r = requests.get(url=url, headers=headers)

        try:
            products = json.loads(r.text)['products']
        except json.decoder.JSONDecodeError:
            return auctions

        for product in products:

            # If search_in_desc, search in description as well
            if self.search_in_desc:
                if (self.search_term.lower() not in product['vendor'].lower() and
                        self.search_term.lower() not in product['body_html'].lower()):
                    continue
            if not self.search_in_desc:
                if self.search_term.lower() not in product['vendor'].lower():
                    continue

            title = f"{product['vendor']} - {product['title']}"
            auction_id = str(product['id'])
            link = f'https://www.{self.domain}/products/' + product['handle']
            image_link = product['images'][0]['src']
            start_date = dateparser.parse(product['created_at'])

            _variants = '\n'.join([f"${x['price']} - {x['title']}" for x in product['variants']])
            description = f"{_variants}\n\n{product['body_html']}"

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link,
                    'start_date': start_date
                }))

        return auctions
