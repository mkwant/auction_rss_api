import hashlib
from abc import ABC, abstractmethod
from typing import List

import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class GreedbagExtractor(AuctionExtractor, ABC):
    """A base class for Greedbag sites."""

    @property
    @abstractmethod
    def site_name(self) -> str:
        """The name of the Greedbag site, i.e 'soisong' for 'soisong.greedbag.com'."""
        ...

    @property
    def search_link(self) -> str:
        return f'https://{self.site_name}.greedbag.com'

    @property
    def site_desc(self) -> str:
        return f'{self.site_name}.greedbag.com'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = requests.get(self.search_link)
        soup = BeautifulSoup(r.content, features="html.parser")

        products = soup.select('div.hproduct')
        for product in products:
            _title = product.select_one('h2.album')
            if _title:
                _title = _title.text.strip()
            _artist = product.select_one('h3.artist')
            if _artist:
                _artist = _artist.text.strip()
            title = f'{_artist} - {_title}'
            link = self.search_link + str(product.select_one('a')['href'])  # ty: ignore[non-subscriptable]

            _image = product.select_one('img')
            if _image:
                image_link = _image['src']
            else:
                image_link = None

            _desc = product.select_one('div.description')
            if _desc:
                _description = _desc.text.strip()
            _price = product.select_one('div.line-details')
            if _price:
                _price = _price.text.strip()
            description = f"{_price}\n\n{_desc}"
            auction_id = hashlib.md5(link.encode('utf-8')).hexdigest()

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                ))

        return auctions
