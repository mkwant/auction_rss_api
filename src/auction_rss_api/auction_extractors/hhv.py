import json
import re
from typing import List
from urllib.parse import quote_plus, urlsplit, urlunsplit

from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


class HHV(AuctionExtractorAsync):
    @property
    def search_link(self) -> str:
        return f"https://www.hhv.de/en/records/catalog/filter/search-N5ST1?term={quote_plus(self.search_term)}"

    @property
    def site_desc(self) -> str:
        return "HHV (2nd hand)"

    async def _render(self) -> str:
        page = await self.browser.new_page()
        try:
            await page.goto(self.search_link, wait_until="domcontentloaded")

            # The JS challenge page reloads itself; wait for the real result list
            await page.wait_for_selector('[data-highlight-name="Artikelliste"]', timeout=20_000)

            # Force all lazy item frames to load without scrolling
            await page.evaluate("""
                                () => document.querySelectorAll('turbo-frame[loading="lazy"]')
                                    .forEach(f => f.setAttribute('loading', 'eager'))
                                """)

            # Wait until no item frame still shows its loader
            await page.wait_for_function(
                """
                                         () => {
                                             const f = [...document.querySelectorAll(
                                                 'turbo-frame.item--shared--gallery-entry--base-component')];
                                             return f.length > 0 &&
                                                 f.every(x => !x.querySelector('.shared--loader--base-component'));
                                         }
                                         """,
                timeout=30_000,
            )

            return await page.content()
        finally:
            await page.close()

    async def get_auctions(self) -> List[Auction]:
        html = await self._render()
        soup = BeautifulSoup(markup=html, features="html.parser")

        items = []
        for frame in soup.select("turbo-frame.item--shared--gallery-entry--base-component"):
            tracking = frame.find("hhv-tracking", attrs={"data-google-analytics-tracking-data": True})
            link_tag = frame.find("a", href=True)
            img = frame.find("img")
            if not (tracking and link_tag):
                continue  # frame never finished loading

            ga = json.loads(tracking["data-google-analytics-tracking-data"])

            parts = urlsplit(link_tag["href"])
            link = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))  # drop ?pquid=...

            fmt = frame.select_one(".line.price .format")
            cond = frame.select_one(".line.feature .used_vinyl .description")

            lines = [f"EUR {ga['price']:.2f}"]
            if ga.get("item_brand"):
                lines.append(ga["item_brand"])
            if fmt:
                lines.append(fmt.get_text(" ", strip=True))
            if cond:
                lines.append(re.sub(r"\s+", " ", cond.get_text(" ", strip=True)))

            items.append(
                Auction(
                    auction_id=ga["item_id"],
                    description="\n".join(lines),
                    image_link=img["src"] if img else "",
                    link=link,
                    title=ga["item_name"],
                )
            )
        return items
