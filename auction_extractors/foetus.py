from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Foetus(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.foetus.org/content/shop/'

    @property
    def site_desc(self) -> str:
        return "Foetus.org"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = httpx.get(url=self.search_link)

        soup = BeautifulSoup(markup=r.text, features="html.parser")
        items = soup.select(selector='div.default_product_display')
        for item in items:

            auction_id = item.select_one('form')['id']

            _type = item['class'][-2].rstrip('s').replace('-', ' ').capitalize()
            _title = item.select_one('h2.prodtitle').text.strip()
            title = f'{_title} ({_type})'

            image_link = item.select_one('img.product_image')['src']

            _cat_nr = item.select_one('small').text.strip()
            _desc_1 = item.select_one('div.wpsc_description').text.strip()

            try:
                _desc_2 = item.select_one('div.additional_description').text.strip()
            except AttributeError:
                _desc_2 = ""
            description = f'{_cat_nr}\n\n{_desc_1}{_desc_2}'

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=self.search_link,
                    image_link=image_link,
                    description=description,
                )
            )
        return auctions
