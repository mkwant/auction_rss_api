from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class GumTree(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.gumtree.com/search?q={self.search_term}&sort=date"

    @property
    def site_desc(self) -> str:
        return "Gumtree"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = "https://www.gumtree.com/search"
        params = {"q": self.search_term, "sort": "date"}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"}
        r = httpx.get(url=url, params=params, headers=headers)
        r.raise_for_status()
        if r.status_code == 247:
            raise ConnectionError("Received HTTP Error 247")
        soup = BeautifulSoup(r.text, features="html.parser")
        items = soup.select('a.e25keea22')

        for item in items:
            link = item['href']
            auction_id = link.split('/')[-1]

            try:
                image_link = item.select_one('img')['src']
            except KeyError:
                image_link = item.select_one('img')['data-src']
            title = item.select_one('div.e25keea18').text
            _desc = item.select_one('p.e25keea17').text
            _location = item.select_one('div[data-q="tile-location"]').text
            _price = item.select_one('div[data-q="tile-price"]').text
            description = f"{_desc}\n\n{_price}\n\n{_location}"

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link
                }))

        return auctions
