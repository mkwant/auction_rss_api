import urllib.parse
from typing import List

import curl_cffi
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Delcampe(AuctionExtractor):
    search_term: str
    URL: str = 'https://www.delcampe.net/en_GB/collectables/search'

    @property
    def site_desc(self) -> str:
        return 'Delcampe'

    @property
    def search_link(self) -> str:
        return f'https://www.delcampe.net/en_GB/collectables/search?term={self.search_term}'

    def _get_auctions(self) -> ResultSet:
        params = {'term': self.search_term}

        r = curl_cffi.get(url=self.URL, params=params, impersonate='firefox')
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.content, features='html.parser')

        site_auctions = soup.select('div.item-bloc')
        return site_auctions

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for auction in self._get_auctions():
            try:
                image_link = auction.select_one('a.img-view')['href']
            except TypeError:
                image_link = auction.select_one('a.img-link')['href']
            try:
                auction_id = auction.select_onfe('a.img-view')['data-item-id']
            except TypeError:
                auction_id = auction.select_one('a.img-link')['data-item-id']
            link = f"https://www.delcampe.net{auction.select_one('a.item-link')['href']}"
            title = auction.select_one('h2.item-title').text
            _price = auction.select_one('strong.item-price').text
            _item_type = auction.select_one('div.selling-type')['title']
            desc = f'{_item_type} | {_price}'

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=desc,
                    image_link=image_link,
                    link=link,
                    title=title,
                )
            )

        return auctions
