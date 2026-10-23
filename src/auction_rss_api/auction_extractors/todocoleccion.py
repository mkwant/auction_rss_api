import asyncio
import logging
import tempfile
from pathlib import Path
from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync

logger = logging.getLogger(__name__)

# Only one Todocoleccion page at a time: easier on a Pi and less likely to
# get the Cloudflare clearance revoked by a burst of parallel sessions.
_FETCH_LOCK = asyncio.Lock()


class Todocoleccion(AuctionExtractorAsync):
    search_term: str
    URL: str = "https://en.todocoleccion.net/buscador"
    BASE: str = "https://en.todocoleccion.net"

    @property
    def site_desc(self) -> str:
        return "Todocoleccion"

    @property
    def search_link(self) -> str:
        return f"{self.URL}?{urlencode({'O': 'r', 'bu': self.search_term})}"

    @staticmethod
    async def _dump_debug(page: Page) -> None:
        """Save what the browser saw when the challenge wasn't solved."""
        try:
            debug_dir = Path(tempfile.gettempdir())
            png = debug_dir / "todocoleccion_challenge.png"
            html = debug_dir / "todocoleccion_challenge.html"
            await page.screenshot(path=str(png))
            html.write_text(await page.content(), encoding="utf-8")
            logger.error("Todocoleccion challenge dump saved to %s and %s", png, html)
        except Exception:
            logger.exception("Could not save Todocoleccion debug dump")

    async def _fetch_html(self, search_term: str) -> str:
        url = f"{self.URL}?{urlencode({'O': 'r', 'bu': search_term, 'Navegacion': 'i'})}"

        async with _FETCH_LOCK:
            page = await self.browser.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60_000)

                # Wait for the Cloudflare "Just a moment..." interstitial to clear.
                # Don't wait on div.card-lote: a search with zero results would time out.
                try:
                    await page.wait_for_function(
                        "() => !document.title.includes('Just a moment')",
                        timeout=60_000,
                    )
                except PlaywrightTimeoutError:
                    await self._dump_debug(page)
                    raise RuntimeError(
                        "Todocoleccion: Cloudflare challenge was not solved in time"
                    )

                try:
                    await page.wait_for_load_state("networkidle", timeout=15_000)
                except PlaywrightTimeoutError:
                    pass

                return await page.content()
            finally:
                await page.close()

    async def get_auctions(self) -> List[Auction]:
        html = await self._fetch_html(self.search_term)
        soup = BeautifulSoup(html, "html.parser")

        auctions = []

        for card in soup.select("div.card-lote"):
            info = card.select_one("a.js-lot-titles")
            if info is None:
                continue

            img = card.select_one("img")
            image_link = ""
            if img is not None:
                image_link = (img.get("src") or img.get("data-src") or "").split("?")[0]

            title = info.text.strip()
            link = self.BASE + info["href"]
            unique_id = info["id"].replace("lot-title-", "")

            price_el = card.select_one("span.fs-18")
            price = price_el.text.strip() if price_el else ""

            seller_block = card.select_one("p.lote-vendedor")
            seller_span = seller_block.select_one("span") if seller_block else None
            seller = seller_span.text.strip() if seller_span else ""

            type_block = card.select_one("a._lote_item-img-footerbox")
            item_type = type_block.text.strip() if type_block else "Buy now"

            category_el = card.select_one("a.fs-14")
            category = category_el.text.strip() if category_el else ""

            desc = f"{price} | {item_type} | {category}"

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    description=desc,
                    image_link=image_link,
                    link=link,
                    title=title,
                    seller=seller,
                )
            )

        return auctions
