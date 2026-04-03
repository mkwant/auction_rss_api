from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class MontreuxJazzShop(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.montreuxjazzshop.com/en/?s={self.search_term}&_tri=new"

    @property
    def site_desc(self) -> str:
        return "MontreuxJazzShop"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.montreuxjazzshop.com/en/'
        params = {
            's': self.search_term,
            '_tri': 'new',
        }

        r = httpx.get(url=url, params=params)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features='html.parser')

        items = soup.select('div.product')
        for item in items:
            try:
                auction_id = item.select_one('div.wp-block-button > a')['data-product_id']
            except TypeError:
                auction_id = item.select_one('div.wp-block-button > button')['data-product_id']

            link = item.select_one('a')['href']
            image_link = item.select_one('img')['srcset'].split(',')[-1].split()[0]
            title = item.select_one('div.mb-3').text.strip()
            description = item.select_one('span.amount').text.strip()

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
