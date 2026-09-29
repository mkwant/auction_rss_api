from typing import List

from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


class SubpopExclusives(AuctionExtractorAsync):
    @property
    def search_link(self) -> str:
        return "https://europe.subpop.com/losers"

    @property
    def site_desc(self) -> str:
        return "Subpop Exclusives"

    async def get_auctions(self) -> List[Auction]:
        page = await self.browser.new_page()

        try:
            await page.goto(
                self.search_link,
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await page.wait_for_function(
                """() => {
                    return document.cookie.includes("aws-waf-token")
                        || performance.getEntriesByType("navigation")
                            .some(e => e.type === "reload");
                }""",
                timeout=30_000,
            )

            try:
                await page.wait_for_load_state(
                    "networkidle",
                    timeout=30_000,
                )
            except PlaywrightTimeoutError:
                await page.wait_for_load_state("domcontentloaded")

            html = await page.content()

        finally:
            await page.close()

        soup = BeautifulSoup(html, "html.parser")

        auctions = []

        for item in soup.select("ul.product-list > li"):
            unique_id = str(item["id"])

            link = "https://europe.subpop.com" + item.select_one("a")["href"]

            image_link = item.select_one("div.product-image-box img")["src"].replace("/s/", "/b/").replace("/l/", "/b/")

            artist = item.select_one("dd.artist").text.strip()
            title = item.select_one("dd.release-title").text.strip()

            extra_format = item.select_one("span.extra-format")

            if extra_format:
                title = f"{artist} - {title} ({extra_format.text.strip()})"
            else:
                title = f"{artist} - {title}"

            price = item.select_one("span.price").text.strip()
            label = item.select_one("dd.label").text.strip()
            release_date = item.select_one("dd.product-release-date").text.strip()

            description = f"Price: {price}\nLabel: {label}\nRelease Date: {release_date}"

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    link=link,
                    image_link=image_link,
                    title=title,
                    description=description,
                )
            )

        return auctions
