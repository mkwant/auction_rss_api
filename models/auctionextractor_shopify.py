import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Sequence

import cloudscraper
import dateparser
import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends
from fastapi_rss import RSSResponse

from app.dependencies import Translate
from models.auction import Auction
from models.auctionextractor import AuctionExtractor
from routers.logger import LoggedRoute


@dataclass
class CommonQueryParams:
    search_term: str


router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=RSSResponse,
    dependencies=[Depends(CommonQueryParams)],
    tags=['Shopify']
)


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

    dependencies: list[Depends] = []

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
            link = f'https://{self.domain}{item['product']['url']}'
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

    # TODO: Import classes using importlib, making sure they are imported before the routes are added.
    #  https://gist.github.com/dorneanu/cce1cd6711969d581873a88e0257e312
    #  https://python-forum.io/thread-7923.html
    # TODO: Move CommonQueryParams class
    # TODO: Figure out more complicated endpoints (eBay, Yahoo Japan, etc) - make `feed` func a part of the ABC?

    def create_route(self) -> None:
        # async def feed() -> RSSResponse:
        #     return self.search()
        route_name = self.domain.split('.')[0].lower()
        router.add_api_route(
            path=f'/{route_name}',
            endpoint=self.search,
            methods=["GET"],
            dependencies=self.dependencies,
            # dependencies=[Depends(Translate)],
            summary=f"Rss feed for {self.site_desc}",
            description=f"Returns an RSS feed for {self.site_desc} ({self.domain}).",
        )
