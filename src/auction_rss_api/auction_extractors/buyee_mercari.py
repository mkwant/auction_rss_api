from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


class BuyeeMercari(AuctionExtractorAsync):

    @property
    def search_link(self) -> str:
        return f"https://buyee.jp/mercari/search?limit=100&lang=en&page=1&searchType=filter&order-sort=desc-created_time&keyword={self.search_term}&currencyCode=EUR"

    @property
    def site_desc(self) -> str:
        return 'Buyee (Mercari)'

    async def get_auctions(self) -> List[Auction]:
        auctions = []

        link = 'https://buyee.jp/mercari/search'
        params = {
            'limit': 100,
            'keyword': self.search_term,
            'order-sort': 'desc-created_time',
            'currencyCode': 'EUR',
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        page = await self.browser.new_page()
        await page.set_extra_http_headers(headers)

        try:
            await page.goto(url=f"{link}?{urlencode(params)}", wait_until="networkidle")
            html = await page.content()

        finally:
            await page.close()

        soup = BeautifulSoup(markup=html, features='html.parser')

        items = soup.select('ul.item-lists>li.list')
        for item in items:
            link = 'https://buyee.jp' + item.select_one('a')['href']
            auction_id = link.split('?')[0].split('/')[-1]
            _image_link = item.select_one('img')['data-bind'].replace('\n', ' ').split('\'')[1].replace('/small/',
                                                                                                        '/large/')
            image_link = f"https:{_image_link.split('?')[0]}"

            title = item.select_one('h2.name').text.strip()

            _price_yen = item.select_one('p.price').text.strip()
            _price_eur = item.select_one('p.price-fx').text.strip()
            try:
                _sold_out = item.select_one('div.soldOut__text').text.strip()
                description = f"{_sold_out}\n{_price_yen} {_price_eur}"
            except AttributeError:
                description = f"{_price_yen} {_price_eur}"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    link=link,
                    image_link=image_link,
                    title=title,
                    description=description,
                )
            )

        return auctions
