from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class SubpopExclusives(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://europe.subpop.com/losers"

    @property
    def site_desc(self) -> str:
        return "Subpop Exclusives"

    def get_auctions(self) -> list[Auction]:
        return []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url=self.search_link, wait_until="domcontentloaded")

            page.wait_for_function(
                expression="""() => {
                    return document.cookie.includes("aws-waf-token")
                        || performance.getEntriesByType("navigation")
                            .some(e => e.type === "reload");
                }""",
                timeout=30_000,
            )

            try:
                page.wait_for_load_state(state="networkidle", timeout=30_000)
            except PlaywrightTimeoutError:
                page.wait_for_load_state("domcontentloaded")

            html = page.content()

        soup = BeautifulSoup(markup=html, features="html.parser")
        items = soup.select('ul.product-list>li')

        auctions = []

        for item in items:
            unique_id = str(item['id'])
            link = 'https://europe.subpop.com' + item.select_one('a')['href']
            image_link = item.select_one('div.product-image-box img')['src'].replace("/l/", "/b/")

            _artist = item.select_one('dd.artist').text.strip()
            _title = item.select_one('dd.release-title').text.strip()

            try:
                _desc = item.select_one('span.extra-format').text.strip()
                title = f"{_artist} - {_title} ({_desc})"
            except AttributeError:
                title = f"{_artist} - {_title}"

            _price = item.select_one('span.price').text.strip()
            _label = item.select_one('dd.label').text.strip()
            _reldate = item.select_one('dd.product-release-date').text.strip()
            description = f"Price: {_price}\nLabel: {_label}\nRelease Date: {_reldate}"

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
