from typing import List

import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class MagicbusExtractor(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://magicbusrecords.net/?orderby=date&paged=1&s={self.search_term}&post_type=product'

    @property
    def site_desc(self) -> str:
        return 'Magicbus Records'

    def get_auctions(self) -> List[Auction]:

        auctions = []
        r = requests.get(self.search_link)
        r.raise_for_status()

        soup = BeautifulSoup(r.content, features='html.parser')

        items = soup.select('li.product')
        for item in items:
            title = item.select_one('h3.wp-block-post-title').text.strip()
            link = item.select_one('h3.wp-block-post-title>a')['href']

            try:
                raw_img_link = item.select_one('img')['data-opt-src']
            except KeyError:
                raw_img_link = item.select_one('img')['src']
            print(raw_img_link)
            try:
                image_link = 'https' + raw_img_link.split('https')[2].replace('avif', 'jpg')
            except IndexError:
                image_link = raw_img_link.replace('avif', 'jpg')

            auction_id = link.split('/')[-2]

            try:
                _desc = item.select_one('div.taxonomy-product_tag').text.strip()
            except AttributeError:
                _desc = ''

            try:
                _price = item.select_one('span.amount').text.strip()
            except AttributeError:
                _price = 'Make an offer'

            description = '\n'.join([_desc, _price]).strip()

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link,
                }))

        return auctions
