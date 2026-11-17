from typing import List

import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Imusic(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://imusic.com/page/search?_form=searchForm&advanced=1&combined={self.search_term}&sort=releaseDateDesc"

    @property
    def site_desc(self) -> str:
        return "Imusic"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = httpx2.get(url=self.search_link, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features="html.parser")

        for item in soup.select("article.search-teaser"):
            link_el = item.select_one("a.search-teaser__link")
            if link_el is None:
                continue

            _slug = link_el["href"]  # e.g. /books/9781917274227/some-slug
            auction_id = _slug.split("/")[2]
            link = "https://imusic.com" + _slug

            title_el = item.select_one(".item-teaser__title a")
            title = title_el.get_text(strip=True) if title_el else link_el.get("title", "")
            artist_el = item.select_one(".item-teaser__artist")
            if artist_el:
                title = f"{artist_el.get_text(strip=True)} - {title}"

            img = item.select_one("img.item-cover")
            image_link = img["src"].replace("scaled", "original") if img else ""

            price_el = item.select_one(".teaser-cta__price")
            _price = price_el.get_text(strip=True) if price_el else ""

            fmt_el = item.select_one(".item-teaser__format")
            _format = fmt_el.get_text(strip=True) if fmt_el else ""

            btn = item.select_one("button.teaser-cta")
            _note = btn.get("title", "") if btn else ""

            description = f"{_price}\n{_format}\n\n{_note}".strip()

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
