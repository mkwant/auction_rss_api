from typing import List

import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class MemorabiliaUk(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.memorabilia-uk.co.uk/p/{self.search_term}"

    @property
    def site_desc(self) -> str:
        return "Memorabilia UK"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = requests.get(url=self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, features='html.parser')

        items = soup.select('div.items__item')
        for item in items:
            auction_id = item.select_one('p.items__item__reference').text.replace('Reference Number. ', '').strip()
            link = 'https://www.memorabilia-uk.co.uk' + item.select_one('a')['href']
            image_link = 'https://www.memorabilia-uk.co.uk' + item.select_one('img')['src']
            title = item.select_one('p.items__item__name').text.strip()

            try:
                _price = item.select_one('div.items__item__price').text.strip()
            except AttributeError:
                _price = item.select_one('div.items__item__price_no_price').text.strip()
            _desc = item.select_one('p:not([class])').text

            desc = f"{_price}\n\n{_desc}"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=desc,
                    image_link=image_link,
                    link=link,
                    title=title
                )
            )

        return auctions
