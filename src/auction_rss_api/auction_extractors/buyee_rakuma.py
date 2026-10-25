from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_rss_api.auction_extractors.buyee_fetch import fetch_buyee_html
from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


class BuyeeRakuma(AuctionExtractorAsync):
    search_term: str

    @property
    def site_desc(self) -> str:
        return 'Buyee (Rakuma)'

    @property
    def search_link(self) -> str:
        return f'https://buyee.jp/rakuma/search?keyword={self.search_term}&status=all'

    async def _get_auctions(self) -> ResultSet:
        base = 'https://buyee.jp/rakuma/search'
        params = {
            'keyword': self.search_term,
            'status': 'all',
        }

        html = await fetch_buyee_html(
            self.browser,
            f'{base}?{urlencode(params)}',
            ready_selector='ul.item-lists > li',
        )

        soup = BeautifulSoup(markup=html, features='html.parser')
        return soup.select('ul.item-lists > li')

    async def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in await self._get_auctions():
            title = item.select_one('h2.name').text.strip()

            price_yen = item.select_one('p.price').text.strip()
            price_eur = item.select_one('p.price-fx').text.strip()
            description = f'{price_yen} {price_eur}'

            _link = item.select_one('a')['href'].split('?')[0]
            link = f'https://buyee.jp{_link}'
            auction_id = _link.split('/')[-1]

            _image_link = (
                item.select_one('img')['data-bind']
                .replace('\n', ' ')
                .split("'")[1]
                .replace('/s/', '/l/')
            )
            image_link = f"https:{_image_link.split('?')[0]}"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title,
                )
            )

        return auctions
