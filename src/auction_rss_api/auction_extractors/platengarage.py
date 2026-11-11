from typing import List

from bs4 import BeautifulSoup
from playwright.async_api import Page

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


class PlatenGarage(AuctionExtractorAsync):
    @property
    def search_link(self) -> str:
        return f"https://www.deplatengarage.nl/search/?search={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "PlatenGarage"

    async def get_auctions(self) -> List[Auction]:
        auctions = []

        page: Page = await self.browser.new_page()

        try:
            await page.goto(
                url=self.search_link,
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await page.wait_for_selector(
                selector="ul.products>li",
                timeout=30_000,
            )

            html = await page.content()

        finally:
            await page.close()

        soup = BeautifulSoup(markup=html, features='html.parser')
        products = soup.select('ul.products>li')

        for product in products:
            unique_id = str(product['id'])
            title = product.select_one('a.title').text.strip()
            link = str(product.select_one('a.title')['href'])
            image_link = product.select_one('img')['src'].replace('/article/', '/full/')
            _price = product.select_one('span.pricetag').text.strip()
            _desc = product.select_one('p.desc').text.strip()
            description = f"{_price}\n\n{_desc}"

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
