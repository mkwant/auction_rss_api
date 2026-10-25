from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from auction_rss_api.auction_extractors.buyee_fetch import fetch_buyee_html
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
        base = f'https://buyee.jp/item/search/query/{self.search_term}'
        params = {
            'sort': 'end',
            'order': 'd',
            'conversionType': 'top_page_search',
            'new': 1,
            'translationType': 1,
        }
        return await fetch_buyee_html(
            self.browser,
            f'{base}?{urlencode(params)}',
            ready_selector='div.itemCard__item',
        )

    async def get_auctions(self) -> List[Auction]:
        html = await self._get_page()
        soup = BeautifulSoup(markup=html, features='html.parser')

        auctions = []

        for auction in soup.select('div.itemCard__item'):
            title = auction.select_one('div.itemCard__itemName').text.strip()
            _url_ext = auction.select_one('div.itemCard__itemName>a')['href'].split('?')[0]
            link = f'https://buyee.jp{_url_ext}'
            auction_id = _url_ext.split('/')[-1]

            img = auction.select_one('img.g-thumbnail__image')
            image_link = (img.get('data-src') or img['src']).split('?')[0]

            _auction_price = auction.select_one('div.g-priceDetails').get_text(separator=' ', strip=True)

            days_left = auction.select_one('li.itemCard__infoItem>span.g-text--attention')
            if days_left:
                description = (
                    f'<b>{_auction_price}</b><br>'
                    f'<b>Time left:</b> {days_left.text.strip()}<br>'
                )
            else:
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
