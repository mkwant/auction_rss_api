import hashlib
from typing import List

import curl_cffi
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class HouseOfMythology(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://store.houseofmythology.com'

    @property
    def site_desc(self) -> str:
        return 'House Of Mythology'

    def get_auctions(self) -> List[Auction]:
        r = curl_cffi.get(url=self.search_link, impersonate="chrome")
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')

        auctions = []

        products = soup.select('div.row_product')
        for product in products:
            _slug = str(product.select_one('a')['href'])
            unique_id = hashlib.md5(_slug.encode('utf-8')).hexdigest()
            title = " ".join(product.select_one('span.productTitle').text.strip().split())
            link = self.search_link + _slug
            image_link = product.select_one('img')['src']
            description = product.select_one('span.price').text.strip()

            if self.search_term:
                if self.search_term.lower() not in title.lower():
                    continue

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title,
                )
            )

        return auctions
