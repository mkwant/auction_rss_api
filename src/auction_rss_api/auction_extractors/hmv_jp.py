from typing import List

from bs4 import BeautifulSoup
from playwright.async_api import Page

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


class HMVJapan(AuctionExtractorAsync):
    @property
    def search_link(self) -> str:
        return f'https://www.hmv.co.jp/en/search/advanced_1/category_1%2C2%2C3%2C4%2C5%2C7%2C9%2C10%2C23%2C24%2C50%2C106/formattype_1/keyword_{self.search_term}/sort_datedesc/target_ALL/'

    @property
    def site_desc(self) -> str:
        return 'HMV Japan'

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
                selector="ul.resultList>li.list",
                timeout=30_000,
            )

            html = await page.content()

        finally:
            await page.close()

        soup = BeautifulSoup(markup=html, features='html.parser')
        products = soup.select('ul.resultList>li.list')

        for product in products:
            _artist = product.select_one('p.name').text.strip()
            _title = product.select_one('h3.title').text.strip()
            title = f"{_artist} - {_title}"
            try:
                auction_id = product.select_one('button.js-favoritBtn')['data-sku']
            except TypeError:
                auction_id = product.select_one('div.favoritBtn>a.favorit')['data-async'].split(':')[1].rstrip(';')

            _price = product.select_one('div.price').text.strip()
            _release_date = product.select_one('div.other').text.strip()

            description = f"{_price}\n\n{_release_date}"

            link = str(product.select_one('h3.title>a')['href'])
            if not link.startswith('https'):
                link = 'https://www.hmv.co.jp' + link

            image_link = product.select_one('img')['src'].replace('/190/', '/400/')

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link
                }))

        return auctions
