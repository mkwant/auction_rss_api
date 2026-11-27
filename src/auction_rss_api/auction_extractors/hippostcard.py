from typing import Dict, List
from urllib.parse import quote_plus, urljoin, urlparse

from bs4 import BeautifulSoup, Tag
from playwright.async_api import Page

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync

BASE_URL = "https://www.hippostcard.com"

# Listing images are lazy-loaded in the DOM (background-image stays empty until a
# tile is scrolled into view), but the Nuxt SSR state already holds every listing
# with its `images` array.
#
# Camoufox runs page.evaluate() in an isolated world, where the page's own globals
# (window.__NUXT__) are invisible. The "mw:" prefix evaluates in the main world.
_JS_COLLECT_IMAGES = """mw:(() => {
  const out = {};
  const seen = new Set();
  const walk = (o) => {
    if (!o || typeof o !== 'object' || seen.has(o)) return;
    seen.add(o);
    if (Array.isArray(o)) { o.forEach(walk); return; }
    if (o.id != null && Array.isArray(o.images) && typeof o.images[0] === 'string') {
      out[String(o.id)] = o.images;
    }
    Object.values(o).forEach(walk);
  };
  walk(window.__NUXT__);
  return out;
})()"""

# Fallback: read the lazy-loaded background-image of each tile (DOM is shared by
# both worlds, so no "mw:" needed). Tiles must have been scrolled into view first.
_JS_TILE_IMAGES = """() => {
  const out = {};
  document.querySelectorAll('a.r-gallery-tile').forEach(t => {
    const id = (t.getAttribute('href') || '').split('?')[0].replace(/\\/+$/, '').split('/').pop();
    const el = t.querySelector('.v-image__image');
    const m = el && getComputedStyle(el).backgroundImage.match(/url\\(["']?(.*?)["']?\\)/);
    if (id && m && m[1]) out[id] = [m[1]];
  });
  return out;
}"""


class HipPostcard(AuctionExtractorAsync):
    @property
    def search_link(self) -> str:
        return f"{BASE_URL}/search?keywords={quote_plus(self.search_term)}"

    @property
    def site_desc(self) -> str:
        return "HipPostcard"

    async def get_auctions(self) -> List[Auction]:
        return []

    # async def get_auctions(self) -> List[Auction]:
    #     page: Page = await self.browser.new_page()
    #
    #     try:
    #         await page.goto(
    #             url=self.search_link,
    #             wait_until="domcontentloaded",
    #             timeout=30_000,
    #         )
    #
    #         # Also covers the Cloudflare "Just a moment..." interstitial: the tiles only
    #         # exist once the real page has loaded.
    #         await page.wait_for_selector(
    #             selector="a.r-gallery-tile",
    #             timeout=45_000,
    #         )
    #
    #         # Opt out of image blocking
    #         await page.route("**/*", lambda route: route.continue_())
    #
    #         html = await page.content()
    #
    #         images: Dict[str, List[str]] = {}
    #         try:
    #             images = await page.evaluate(_JS_COLLECT_IMAGES) or {}
    #         except Exception:
    #             pass
    #
    #         if not images:
    #             # Fallback: scroll so the lazy tiles load, then read their styles.
    #             for _ in range(30):
    #                 await page.mouse.wheel(0, 800)
    #                 await page.wait_for_timeout(300)
    #             await page.wait_for_timeout(1_000)
    #             try:
    #                 images = await page.evaluate(_JS_TILE_IMAGES) or {}
    #             except Exception:
    #                 pass

        # finally:
        #     await page.close()
        #
        # return self._parse(html, images)

    @staticmethod
    def _text(el: Tag | None) -> str:
        return el.get_text(" ", strip=True) if el else ""

    def _parse(self, html: str, images: Dict[str, List[str]]) -> List[Auction]:
        soup = BeautifulSoup(markup=html, features="html.parser")
        auctions = []

        for tile in soup.select("a.r-gallery-tile"):
            path = urlparse(str(tile["href"])).path  # drop ?sponsored=1 tracking param
            unique_id = path.rstrip("/").rsplit("/", 1)[-1]
            title = self._text(tile.select_one(".r-gallery-tile__title"))
            link = urljoin(BASE_URL, path)
            image_link = (images.get(unique_id) or [None])[0]

            price = self._text(tile.select_one(".r-gallery-tile__price"))
            original = self._text(tile.select_one(".r-gallery-tile__original-price"))
            shipping = self._text(tile.select_one(".r-gallery-tile__shipping"))
            best_offer = tile.select_one(".r-gallery-tile__best-offer") is not None

            price_line = f"{price} (was {original})" if original else price
            if best_offer:
                price_line += " or Best Offer"
            description = "\n".join(p for p in (price_line, shipping) if p)

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
