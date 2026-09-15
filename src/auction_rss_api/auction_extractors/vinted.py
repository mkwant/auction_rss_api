from typing import List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Vinted(AuctionExtractor):
    search_term: str
    catalog_id: Optional[int] = None
    search_title_only: bool = True

    @property
    def site_desc(self) -> str:
        return "Vinted"

    @property
    def search_link(self) -> str:
        url = f"https://www.vinted.nl/catalog?search_text={self.search_term}&order=newest_first"
        if self.catalog_id is not None:
            url += f"&catalog[]={self.catalog_id}"
        return url

    def _get_page(self) -> List[dict]:
        url = "https://www.vinted.nl/catalog"

        params = {
            "search_text": self.search_term,
            "order": "newest_first",
        }

        if self.catalog_id is not None:
            params["catalog[]"] = self.catalog_id

        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0"),
            "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://www.vinted.nl/",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
        }

        with httpx.Client(headers=headers, follow_redirects=True, timeout=30) as client:
            r = client.get(url=url, params=params)

        if r.status_code != 200:
            raise RuntimeError(f"Vinted returned HTTP {r.status_code} for {r.url}: {r.text[:500]}")

        soup = BeautifulSoup(markup=r.text, features="html.parser")

        items = []

        for card in soup.select('[data-testid^="product-item-id-"]'):
            test_id = card.get("data-testid", "")

            if not test_id.startswith("product-item-id-"):
                continue

            item_id = test_id.removeprefix("product-item-id-")

            link = card.select_one('[data-testid$="--overlay-link"]')
            title = card.select_one('[data-testid$="--description-title"]')
            price = card.select_one('[data-testid$="--price-text"]')
            image = card.select_one('[data-testid$="--image--img"]')

            if link is None or title is None:
                continue

            items.append(
                {
                    "id": item_id,
                    "title": title.get_text(strip=True),
                    "url": urljoin(
                        "https://www.vinted.nl",
                        link.get("href", ""),
                    ).removesuffix('?referrer=catalog'),
                    "price": (price.get_text(strip=True) if price is not None else ""),
                    "image": (image.get("src") if image is not None else None),
                }
            )

        return items

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in self._get_page():
            if self.search_title_only:
                if self.search_term.lower() not in item["title"].lower():
                    continue

            auctions.append(
                Auction(
                    title=item["title"],
                    auction_id=item["id"],
                    description=item["price"],
                    link=item["url"],
                    image_link=item["image"],
                )
            )

        return auctions
