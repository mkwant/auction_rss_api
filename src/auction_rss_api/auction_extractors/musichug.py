from typing import List

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class MusicHug(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return (
            "https://www.musikhug.ch/de/search/Section1.htm"
            f"?query={self.search_term}"
        )

    @property
    def site_desc(self) -> str:
        return "MusicHug"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0"
            )

            page.goto(url=self.search_link, wait_until="domcontentloaded")
            page.wait_for_selector(selector="article.article-list-item", timeout=30_000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(markup=html, features="html.parser")

        for item in soup.select("article.article-list-item"):
            favorite_button = item.select_one(
                "button.opc-favorite-button"
            )
            title_element = item.select_one("span.list-view")
            link_element = item.select_one("a")
            image_element = item.select_one("img")
            price_element = item.select_one("span.price-basis")

            if not all(
                    [
                        favorite_button,
                        title_element,
                        link_element,
                        image_element,
                    ]
            ):
                continue

            item_id = str(favorite_button["data-op-artno"])

            title = title_element.get_text(strip=True)

            href = link_element["href"]
            link = f"https://www.musikhug.ch{href}"

            image_src = image_element["src"]
            image_link = "https://www.musikhug.ch" + image_src.replace("_M_", "_L_")

            description = (
                price_element.get_text(strip=True)
                if price_element
                else ''
            )

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
