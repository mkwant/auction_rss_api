import hashlib
import re
from typing import List

import curl_cffi
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class EasyLiveAuction(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.easyliveauction.com/catalogue/?searchTerm={self.search_term}&searchOption=3&sortBy=newest&currentPage=1&maxResults=120"

    @property
    def site_desc(self) -> str:
        return "EasyLiveAuction"

    def get_auctions(self) -> List[Auction]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) Gecko/20100101 Firefox/154.0'}
        r = curl_cffi.get(url=self.search_link, headers=headers, impersonate='firefox')
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features="html.parser")

        def clean_text(element) -> str:
            """Normalize whitespace in an HTML element."""
            return re.sub(pattern=r"\s+", repl=" ", string=element.get_text(" ", strip=True))

        items = soup.select("div.grid-lot")

        auctions = []

        for item in items:
            _slug = item.select_one("a")["href"]
            link = "https://www.easyliveauction.com" + _slug
            image_link = item.select_one("img")["src"].replace("_PREVIEW", "")
            unique_id = hashlib.md5(_slug.encode()).hexdigest()

            _lot = clean_text(item.select_one("div.catalogue-description > h4 > a"))
            _title = clean_text(item.select_one("div.catalogue-description > a.no-hover > p"))
            title = f"{_lot}: {_title}"

            _description = item.select_one(".catalogue-description")
            _texts = [
                clean_text(p)
                for p in _description.select(":scope > a.no-hover > p")
                if clean_text(p)
            ]
            _auction_date = next(
                (
                    clean_text(p)
                    for p in _description.select(":scope > small p")
                    if not p.select_one("a")
                ),
                None,
            )
            desc = "\n".join(_texts[1:])

            if _auction_date:
                desc += f"\n{_auction_date}"

            auction_house = clean_text(_description.select_one(':scope > small a[href^="/auctioneers/"]')).removeprefix(
                "by ")

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=desc,
                    seller=auction_house,
                )
            )

        return auctions
