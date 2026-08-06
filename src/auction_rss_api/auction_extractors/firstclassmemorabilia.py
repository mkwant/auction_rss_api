from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class FirstClassMemorabilia(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://firstclassmemorabilia.com/?s={self.search_term}&post_type=product'

    @property
    def site_desc(self) -> str:
        return 'FirstClassMemorabilia'

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(self.search_link)
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('li.product')

        auctions = []

        for item in items:
            unique_id = str(item.select_one('a.button')['data-product_id'])
            title = item.select_one('h2.woocommerce-loop-product__title').text.strip()
            link = str(item.select_one('a')['href'])
            image_link = item.select_one('img')['src'].replace('-300x300', '')
            description = item.select_one('span.price').text.strip()

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
