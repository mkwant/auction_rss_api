from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class DiskUnion(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://diskunion.net/portal/ct/list/0/{self.search_term}/0/0/0/0/50/0'

    @property
    def site_desc(self) -> str:
        return "DiskUnion"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url=self.search_link, timeout=10.0)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('li.searchAll__li')

        auctions = []

        for item in items:

            link = 'https://diskunion.net' + item.select_one('a')['href']
            image_link = 'https:' + item.select_one('img')['src']
            unique_id = link.split('/')[-1]

            _artist = item.select_one('h2.searchAll__artist>a').text.strip()
            _title = item.select_one('h2.searchAll__name>a').text.strip()
            title = f"{_artist} - {_title}"

            try:
                _price = item.select_one('p.u-priceNormal').text.strip()
            except AttributeError:
                _price = item.select_one('p.u-priceBefore').text.strip()

            _desc = item.select_one('p.searchAll__other').text.strip()
            _desc2 = item.select_one('p.searchAll__itemDesc').text.strip()

            try:
                _subtitle = item.select_one('p.searchAll__subTitle').text.strip()
                description = f"{_price}\n\n{_subtitle}\n\n{_desc}\n\n{_desc2}"
            except AttributeError:
                description = f"{_price}\n\n{_desc}\n\n{_desc2}"

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=str(title),
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
