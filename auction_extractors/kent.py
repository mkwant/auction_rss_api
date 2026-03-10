from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Kent(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://kentjapan.com/en/list.php?v=1&w=0&k={self.search_term}&b=1&l=&o=rd&c=&d=&t=&a="

    @property
    def site_desc(self) -> str:
        return "Kent"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://kentjapan.com/en/list.php'
        params = {
            'w': 0,
            'k': self.search_term,
            'o': 'rd',
        }

        r = httpx.get(url=url, params=params, timeout=10.0)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features="html.parser")
        items = soup.select('table[width="630"]')  # outer tables

        for item in items:
            inner_table = item.select_one('table[width="800"]')
            link = 'https://kentjapan.com/en/' + item.select_one('a')['href']
            image_link = 'https://kentjapan.com' + item.select_one('img')['src']
            auction_id = link.split('=')[-1]

            _artist = inner_table.select_one("tr:nth-of-type(1) td:nth-of-type(2) font").text.strip()
            _title = inner_table.select_one("tr:nth-of-type(2) td:nth-of-type(1) a").text.strip()
            title = f"{_artist} - {_title}"

            try:
                _item_type = inner_table.select_one("tr:nth-of-type(2) td:nth-of-type(2) font").text.strip()
            except AttributeError:
                _item_type = "SOLD OUT"
            _label = inner_table.select_one("tr:nth-of-type(3) td:nth-of-type(1) font").text.strip()
            _price = inner_table.select_one("tr:nth-of-type(3) td:nth-of-type(2) font").text.strip()
            _condition = inner_table.select_one("tr:nth-of-type(5) td:nth-of-type(1) font").text.strip()
            _desc = inner_table.select_one("tr:nth-of-type(6) td:nth-of-type(1) font").text.strip()
            description = f"{_price}\nLABEL: {_label}\nCONDITION: {_condition}\nITEM_TYPE: {_item_type}\n\n{_desc}"

            auctions.append(
                Auction(auction_id=auction_id,
                        description=description,
                        image_link=image_link,
                        link=link,
                        title=title,
                        )
            )
        return auctions
