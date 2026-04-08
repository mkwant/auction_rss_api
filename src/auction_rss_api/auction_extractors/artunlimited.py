from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class ArtunLimited(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.artunlimited.com/catalogsearch/result/?q={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "ArtUnlimited"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = "https://www.artunlimited.com/catalogsearch/result/"
        params = {
            "q": self.search_term,
            "limit": 80,
        }

        r = httpx.get(url=url, params=params)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features="html.parser")

        items = soup.select("li.item")
        for item in items:
            item_id = item.select_one("div.sku").text.strip().split()[1]
            _category = item.select_one("div.category-name").text.strip()
            _title = item.select_one("h2.product-name").text.strip()
            _artist = item.select_one("div.artist").text.strip()
            title = f"{_category}: {_title} ({_artist})"

            link = str(item.select_one("h2.product-name>a")["href"])
            image_link = item.select_one("img")["data-highres"].replace("small_image/113x162", "image/400x400")

            _price = item.select_one("span.price").text.strip()
            description = f"{_category}\n{_price}"

            auctions.append(
                Auction(
                    auction_id=item_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
