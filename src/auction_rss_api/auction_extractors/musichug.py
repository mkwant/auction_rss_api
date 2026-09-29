from typing import List

from bs4 import BeautifulSoup
from playwright.async_api import Page

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


class MusicHug(AuctionExtractorAsync):
    @property
    def search_link(self) -> str:
        return f"https://www.musikhug.ch/de/search/Section1.htm?query={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "MusicHug"

    async def get_auctions(self) -> List[Auction]:
        page: Page = await self.browser.new_page()

        try:
            await page.set_extra_http_headers(
                {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0")}
            )

            await page.goto(
                url=self.search_link,
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await page.wait_for_selector(
                selector="article.article-list-item",
                timeout=30_000,
            )

            html = await page.content()

        finally:
            await page.close()

        soup = BeautifulSoup(
            markup=html,
            features="html.parser",
        )

        auctions = []

        for item in soup.select("article.article-list-item"):
            favorite_button = item.select_one("button.opc-favorite-button")
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

            description = price_element.get_text(strip=True) if price_element else ""

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
