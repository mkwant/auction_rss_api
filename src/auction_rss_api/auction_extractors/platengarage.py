from typing import List

import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class PlatenGarage(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.deplatengarage.nl/search/?search={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "PlatenGarage"

    def get_auctions(self) -> List[Auction]:
        client = httpx2.Client()
        r = client.get(url=self.search_link, timeout=10.0)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        auctions = []

        products = soup.select('ul.products>li')
        for product in products:
            unique_id = str(product['id'])
            title = product.select_one('a.title').text.strip()
            link = str(product.select_one('a.title')['href'])
            image_link = product.select_one('img')['src'].replace('/article/', '/full/')
            _price = product.select_one('span.pricetag').text.strip()
            _desc = product.select_one('p.desc').text.strip()
            description = f"{_price}\n\n{_desc}"

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
