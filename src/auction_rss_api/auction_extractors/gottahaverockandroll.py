from typing import List

import curl_cffi
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class GottaHaveRockAndRoll(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.gottahaverockandroll.com/catalog.aspx?searchby=3&searchvalue={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "GottaHaveRockAndRoll"

    def get_auctions(self) -> List[Auction]:
        auctions = []
fix
        url = 'https://www.gottahaverockandroll.com/catalog.aspx'
        params = {
            'searchby': '3',
            'searchvalue': self.search_term,
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0'}

        r = curl_cffi.post(url=url, params=params, headers=headers, timeout=10.0, impersonate='firefox')
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features="html.parser")
        items = soup.select('div.lot')
        for item in items:

            link = item.select_one('span#LotName>a')['href']
            image_link = 'https://www.gottahaverockandroll.com' + item.select_one('div.imageDiv img')['src'].replace(
                '_sm', '_lg')
            auction_id = link.split('-')[-1].replace('.aspx', '')
            title = item.select_one('span#LotName>a').text.strip()
            _lot_nr = item.select_one('span#LotNumber').text.strip()
            _desc = item.select_one('div.lotData').text.strip()
            description = f'LOT {_lot_nr}\n\n{_desc}'

            auctions.append(
                Auction(auction_id=auction_id,
                        description=description,
                        image_link=image_link,
                        link=link,
                        title=title
                        )
            )

        return auctions
