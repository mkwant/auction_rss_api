import json
from typing import List

import dateparser
import requests

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Dais(AuctionExtractor):
    search_in_desc: bool = False

    @property
    def search_link(self) -> str:
        return f"https://www.daisrecords.com/search?q={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "Dais"

    def get_auctions(self) -> List[Auction]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'
        }

        auctions = []

        url = 'https://www.daisrecords.com/products.json?limit=250'
        r = requests.get(url=url, headers=headers)

        products = json.loads(r.text)['products']
        for product in products:

            # If search_in_desc, search in description as well
            if self.search_in_desc:
                if (self.search_term.lower() not in product['vendor'].lower() or
                        self.search_term.lower() not in product['body_html'].lower()):
                    continue
            if not self.search_in_desc:
                if self.search_term.lower() not in product['vendor'].lower():
                    continue

            title = f"{product['vendor']} - {product['title']}"
            auction_id = str(product['id'])
            link = 'https://www.daisrecords.com/products/' + product['handle']
            image_link = product['images'][0]['src']
            start_date = dateparser.parse(product['created_at'])

            _variants = '\n'.join([f"{x['title']} - ${x['price']}" for x in product['variants']])
            description = f"{_variants}\n\n{product['body_html']}"

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link,
                    'start_date': start_date
                }))

        return auctions
