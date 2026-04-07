from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class RRAuction(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.rrauction.com/search/?str={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'RRAuction'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.rrauction.com/search/'
        params = {'str': self.search_term}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0'}

        r = httpx.get(url=url, headers=headers, params=params)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, features='html.parser')
        items = soup.select('div.auction-item')
        for item in items:
            auction_id = item.select_one('div.add')['id']
            link = 'https://www.rrauction.com' + item.select_one('a:nth-of-type(2)')['href']
            image_link = item.select_one('img')['src']
            title = item.select_one('h2.title').text.strip()

            _starting_bid = ' '.join(item.select_one('p.value').text.split())
            _estimate = ' '.join(item.select_one('p.gallery-estimate').text.split())
            _countdown = ' '.join(item.select_one('p.gallery-countdown').text.split())
            description = f"{_starting_bid}\n{_estimate}\n{_countdown}"

            auctions.append(
                Auction(auction_id=auction_id,
                        description=description,
                        image_link=image_link,
                        link=link,
                        title=title
                        )
            )

        return auctions
