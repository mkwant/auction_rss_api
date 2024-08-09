import json
from typing import List

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as date_parse

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class HouseOfMythology(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://store.houseofmythology.com/'

    @property
    def site_desc(self) -> str:
        return 'House Of Mythology'

    def get_auctions(self) -> List[Auction]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'}

        r = requests.get(url=self.search_link, headers=headers)
        soup = BeautifulSoup(r.text, features='html.parser')

        json_str = soup.select_one('default-products')[':products'].split('\'')[1]

        # Escaping unicode characters
        json_str = bytes(json_str, 'utf-8').decode('unicode_escape')

        items = json.loads(json_str)
        auctions = []

        for item in items:

            auction_id = str(item['id'])
            title = f"{item['artist']} - {item['title']}"
            description = f"{item['standardPriceWithSymbol']}\n\n{item['description']}".replace('\\', '')
            image_link = item['image'].replace('\\', '')
            link = f"https://store.houseofmythology.com/product/{item['linkId']}"
            start_date = date_parse(item['location_info']['created_at'])

            if self.search_term.lower() not in title.lower():
                continue

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title,
                    start_date=start_date
                )
            )

        return auctions
