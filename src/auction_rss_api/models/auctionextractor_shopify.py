import json
import re
from abc import ABC, abstractmethod
from typing import List
from urllib.parse import quote_plus

import curl_cffi
import dateparser
from bs4 import BeautifulSoup
from curl_cffi import Response, Session

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor, AuctionExtractorAsync


class ShopifyExtractor(AuctionExtractor, ABC):
    """Base class for Shopify sites. Extracts first 250 items."""

    search_in_desc: bool = False
    collection: str | None = None

    @property
    @abstractmethod
    def domain(self) -> str: ...

    @property
    def search_link(self) -> str:
        if self.collection is not None:
            return f"https://{self.domain}/collections/{self.collection}/search?q={self.search_term}"

        return f"https://{self.domain}/search?q={self.search_term}"

    @staticmethod
    def _create_scraper() -> Session[Response]:
        return curl_cffi.Session(impersonate="firefox")  # noqa

    def get_auctions(self) -> List[Auction]:
        auctions = []

        if self.collection is not None:
            url = f"https://{self.domain}/collections/{self.collection}/products.json?limit=250"
        else:
            url = f"https://{self.domain}/products.json?limit=250"

        with self._create_scraper() as scraper:
            # Get currency using the same session as the product request.
            currency_url = f"https://{self.domain}/cart.js"

            try:
                response = scraper.get(currency_url, timeout=10.0)
                response.raise_for_status()
                currency = response.json()["currency"]
            except Exception:
                currency = "$"

            response = scraper.get(url, timeout=10.0)
            response.raise_for_status()

            try:
                products = response.json()["products"]
            except (ValueError, KeyError):
                return auctions

        for product in products:
            if self.search_term is not None:
                term = self.search_term.lower()

                if self.search_in_desc:
                    if (
                        term not in product["vendor"].lower()
                        and term not in product["body_html"].lower()
                        and term not in product["title"].lower()
                    ):
                        continue
                else:
                    if term not in product["vendor"].lower() and term not in product["title"].lower():
                        continue

            title = f"{product['vendor']} - {product['title']}"
            auction_id = str(product["id"])
            link = f"https://{self.domain}/products/{product['handle']}"

            try:
                image_link = product["images"][0]["src"]
            except (IndexError, KeyError):
                image_link = None

            start_date = dateparser.parse(product["created_at"])

            variants = "\n".join(
                f"{currency} {variant['price']} - {variant['title']}" for variant in product["variants"]
            )

            description = f"{variants}\n\n{product['body_html']}".replace(" - Default Title", "")

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


class ShopifySearchMixin(ABC):
    """Shared, transport-agnostic logic for Shopify search extractors.

    Deliberately does not inherit from AuctionExtractor / AuctionExtractorAsync,
    so it can be combined with either.
    """

    search_term: str  # provided by the AuctionExtractor(Async) base

    @property
    @abstractmethod
    def domain(self) -> str: ...

    @property
    def search_link(self) -> str:
        return f"https://www.{self.domain}/search?q={quote_plus(self.search_term)}&sort_by=created"

    def _parse_auctions(self, html: str) -> List["Auction"]:
        auctions = []

        soup = BeautifulSoup(
            markup=html,
            features="html.parser",
        )

        script = next(
            (
                script.get_text()
                for script in soup.select("script")
                if ('"productVariants"' in script.get_text() and '"events":"' in script.get_text())
            ),
            None,
        )

        if script is None:
            raise ValueError("Could not find Shopify product data")

        json_str = script.split('searchResult\\":')[1].replace(
            '}]]"});})();',
            "",
        )
        json_str = re.sub(
            pattern=r'\\"',
            repl='"',
            string=json_str,
        )
        json_str = re.sub(
            pattern=r'\\(?!["u])',
            repl="",
            string=json_str,
        )

        json_parsed = json.loads(json_str)
        items = json_parsed["productVariants"]

        term = self.search_term.lower()

        for item in items:
            product = item["product"]

            vendor = product["vendor"]
            title = product["title"]

            if term not in vendor.lower() and term not in title.lower():
                continue

            auction_id = product["id"]
            link = f"https://{self.domain}{product['url'].split('?')[0]}"

            try:
                image_link = "https:" + item["image"]["src"]
            except (TypeError, KeyError):
                image_link = None

            price = f"{item['price']['currencyCode']} {item['price']['amount']:.2f}"

            product_type = product["type"]
            variant_title = item["title"]

            description = f"{price}\n\n{product_type}"

            if variant_title != "Default Title":
                description += f"\n\n{variant_title}"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                    seller=vendor,
                )
            )

        return auctions


class ShopifySearchExtractor(ShopifySearchMixin, AuctionExtractor, ABC):
    """Base class for Shopify sites. Builds a feed off a search result."""

    @staticmethod
    def _create_scraper() -> Session[Response]:
        return curl_cffi.Session(impersonate="chrome")  # noqa

    def get_auctions(self) -> List[Auction]:
        with self._create_scraper() as scraper:
            response = scraper.get(
                url=self.search_link,
                timeout=10.0,
            )
            response.raise_for_status()
            html = response.text

        return self._parse_auctions(html)


class ShopifySearchBrowserExtractor(ShopifySearchMixin, AuctionExtractorAsync, ABC):
    """Same as ShopifySearchExtractor, but fetches the page with the Camoufox
    browser provided by the lifespan (for sites that block plain HTTP clients).
    """

    # Navigation timeout in milliseconds.
    browser_timeout_ms: int = 30_000

    async def get_auctions(self) -> List[Auction]:
        # Assumes AuctionExtractorAsync exposes the lifespan object as self.browser
        page = await self.browser.new_page()
        try:
            response = await page.goto(
                url=self.search_link,
                wait_until="domcontentloaded",
                timeout=self.browser_timeout_ms,
            )

            if response is None:
                raise ValueError(f"No response received from {self.search_link}")

            if response.status >= 400:
                raise ValueError(f"HTTP {response.status} fetching {self.search_link}")

            html = await page.content()
        finally:
            await page.close()

        return self._parse_auctions(html)
