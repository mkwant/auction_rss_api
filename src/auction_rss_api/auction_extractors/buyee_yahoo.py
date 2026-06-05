from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


# TODO Multiple pages? / keep in db?


class BuyeeYahoo(AuctionExtractorAsync):
    search_term: str

    @property
    def site_desc(self) -> str:
        return 'Buyee (Yahoo)'

    @property
    def search_link(self) -> str:
        return f'https://buyee.jp/item/search/query/{self.search_term}?sort=end&order=d&new=1&translationType=1'

    async def _get_page(self) -> str:
        """Retrieve search page."""
        url = f'https://buyee.jp/item/search/query/{self.search_term}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        params = {
            'sort': 'end',
            'order': 'd',
            'conversionType': 'top_page_search',
            'new': 1,
            'translationType': 1
        }

        page = await self.browser.new_page()
        await page.set_extra_http_headers(headers)

        try:
            await page.goto(url="https://buyee.jp")
            await page.wait_for_timeout(timeout=3)
            await page.goto(url=f"{url}?{urlencode(params)}", wait_until="domcontentloaded", timeout=10000)
            html = await page.content()

        finally:
            await page.close()

        return html

    async def get_auctions(self) -> List[Auction]:
        html = await self._get_page()
        soup = BeautifulSoup(markup=html, features='html.parser')

        auctions = []

        for auction in soup.select('div.itemCard__item'):
            title = auction.select_one('div.itemCard__itemName').text.strip()
            _url_ext = auction.select_one('div.itemCard__itemName>a')['href'].split('?')[0]
            link = f"https://buyee.jp{_url_ext}"
            auction_id = _url_ext.split('/')[-1]
            try:
                image_link = auction.select_one('img.g-thumbnail__image')['data-src'].split('?')[0]
            except KeyError:
                image_link = auction.select_one('img.g-thumbnail__image')['src'].split('?')[0]
            _auction_price = auction.select('div.g-priceDetails')[0].get_text(separator=' ', strip=True)
            try:
                _auction_days_left = auction.select_one('li.itemCard__infoItem>span.g-text--attention').text
                description = f'<b>{_auction_price}<br><b>Time left:</b> {_auction_days_left}<br>'
            except AttributeError:
                _auction_days_left = '?'
                description = f'<b>{_auction_price}</b>'

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                )
            )

        return auctions
