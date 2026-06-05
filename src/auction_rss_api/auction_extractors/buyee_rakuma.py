from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


# TODO Translate titles -> make async

class BuyeeRakuma(AuctionExtractorAsync):
    search_term: str

    @property
    def site_desc(self) -> str:
        return 'Buyee (Rakuma)'

    @property
    def search_link(self) -> str:
        return f'https://buyee.jp/rakuma/search?keyword={self.search_term}&status=all'

    async def _get_auctions(self) -> ResultSet:
        url = 'https://buyee.jp/rakuma/search'
        params = {
            'keyword': self.search_term,
            'status': 'all'
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}

        page = await self.browser.new_page()
        await page.set_extra_http_headers(headers)

        try:
            await page.goto(url="https://buyee.jp")
            await page.wait_for_timeout(timeout=5)
            await page.goto(url=f"{url}?{urlencode(params)}", wait_until="domcontentloaded", timeout=10000)
            html = await page.content()

        finally:
            await page.close()

        soup = BeautifulSoup(markup=html, features='html.parser')
        return soup.select('ul.item-lists > li')

    async def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in await self._get_auctions():
            title = item.select_one('h2.name').text
            description = f"{item.select_one('p.price').text} {item.select_one('p.price-fx').text}"
            _link = item.select_one('a')['href'].split('?')[0]
            link = f'https://buyee.jp{_link}'
            auction_id = _link.split('/')[-1]
            _image_link = item.select_one('img')['data-bind'].replace('\n', ' ').split('\'')[1].replace('/s/', '/l/')
            image_link = f"https:{_image_link.split('?')[0]}"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title
                )
            )

        return auctions
