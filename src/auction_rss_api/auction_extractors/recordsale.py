import hashlib
from typing import List

import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class RecordSale(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://recordsale.nl/en/?post_type=product&s={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "RecordSale"

    def get_auctions(self) -> List[Auction]:
        client = httpx2.Client()
        r = client.get(url=self.search_link, timeout=10.0)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        products = soup.select('ul.products>li.product')

        auctions = []
        for product in products:
            title = product.select_one('h2.woocommerce-loop-product__title').text.strip()
            link = str(product.select_one('a.woocommerce-loop-product__link')['href'])
            unique_id = hashlib.md5(link.encode()).hexdigest()
            image_link = product.select_one('img.attachment-woocommerce_thumbnail')['src'].replace('-300x300', '')
            description = product.select_one('span.price').text.strip()

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
