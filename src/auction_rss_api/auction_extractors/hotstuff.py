from typing import List

import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class HotStuff(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://hotstuff.se/index.cfm?x=product&pg=1&prSts=0&zpgId=&searchPhrase={self.search_term}&ordBy=add&view="

    @property
    def site_desc(self) -> str:
        return "HotStuff"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = "https://hotstuff.se/index.cfm"
        params = {
            "x": "product",
            "pg": 1,
            "prSts": 1,
            "searchPhrase": self.search_term,
            "ordBy": "add",
        }

        r = httpx2.get(url=url, params=params)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features="html.parser")
        items = soup.select("div.xProductList > div")
        for item in items:
            a = item.select_one("a[href]")
            if a is None:
                continue

            title = a.get("title") or a.get_text(strip=True)
            link = a["href"]
            auction_id = link.rstrip("/").split("/")[-1]

            img = item.select_one("img")
            image_link = ""
            if img is not None:
                image_link = img.get("data-fallback") or img.get("src") or ""

            desc_div = item.select_one("div[title] + div")
            desc = desc_div.get_text(" ", strip=True) if desc_div else title
            price_div = item.select_one("div[title] > div")
            price = price_div.get_text(strip=True) if price_div else ""
            description = f"{desc}\n\n{price}" if price else desc

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
