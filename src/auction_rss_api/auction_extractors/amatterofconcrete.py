from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class AMatterOfConcrete(AuctionExtractor):
    available_only: bool = False

    @property
    def search_link(self) -> str:
        return f"https://amatterofconcrete.com/?s={self.search_term}&post_type=product&dgwt_wcas=1"

    @property
    def site_desc(self) -> str:
        return "A Matter Of Concrete"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://amatterofconcrete.com/'
        params = {
            's': self.search_term,
            'post_type': 'product',
            'dgwt_wcas': 1,
        }

        r = httpx.get(url=url, params=params)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features='html.parser')
        products = soup.select('div.product')
        for product in products:
            title = product.select_one('p.product-title').text.strip()
            link = product.select_one('a')['href']
            image_link = product.select_one('img')['srcset'].split(',')[-1].split()[0]
            auction_id = link.split('/')[-2]
            description = product.select_one('span.wts-price-incl').text.strip()

            if product.select_one('div.out-of-stock-label'):
                if self.available_only:
                    continue
                description += "\n\nOUT OF STOCK"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
