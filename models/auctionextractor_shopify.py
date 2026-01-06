import json
import re
from abc import ABC, abstractmethod
from typing import List

import cloudscraper
import dateparser
import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class ShopifyExtractor(AuctionExtractor, ABC):
    """A base class for Shopify sites. Extracts the first 250 items from a Shopify site."""
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
        scraper = cloudscraper.create_scraper()
        r = scraper.get(url=url, headers=headers)

        try:
            products = json.loads(r.text)['products']
        except json.decoder.JSONDecodeError:
            return auctions

        for product in products:
            if self.search_term is not None:

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
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                    start_date=start_date,
                )
            )

        return auctions


class ShopifySearchExtractor(AuctionExtractor, ABC):
    """A base class for Shopify sites. Builds a feed off a search result."""

    @property
    @abstractmethod
    def domain(self) -> str:
        """The domain of the Shopify site, i.e 'mysite.com'."""
        ...

    @property
    def search_link(self) -> str:
        return f"https://www.{self.domain}/search?q={self.search_term}"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = f'https://{self.domain}/search'
        params = {
            'q': self.search_term,
            'sort_by': 'created',
        }
        r = httpx.get(url=url, params=params, follow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, features='html.parser')

        script = soup.select_one('script#web-pixels-manager-setup').text
        json_str = script.split('searchResult\\":')[1].replace('}]]"});', '')

        json_str = re.sub(pattern=r'\\"', repl='"', string=json_str)  # Replace escaped quotes with actual quotes
        json_str = re.sub(pattern=r'\\(?!")', repl='',
                          string=json_str)  # Remove unnecessary backslashes that aren't escaping quotes

        json_parsed = json.loads(json_str)
        items = json_parsed['productVariants']
        for item in items:
            auction_id = item['product']['id']
            title = item['product']['title']
            link = self.domain + item['product']['url']
            seller = item['product']['vendor']

            try:
                image_link = 'https:' + item['image']['src']
            except TypeError:
                image_link = None

            _price = f'{item['price']['currencyCode']} {item['price']['amount']:.2f}'
            _type = item['product']['type']
            _desc = item['title']
            description = f'{_price}\n\n{_type}'
            if _desc != 'Default Title':
                description += f'\n\n{_desc}'

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                    seller=seller,
                )
            )

        return auctions
