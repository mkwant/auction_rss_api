import datetime
import json
from typing import List

import httpx
import truststore
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor

truststore.inject_into_ssl()  # Use OS trust store


class Vinyleers(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://vinyleers.com/a/search?type=product&options%5Bprefix%5D=last&q={self.search_term}&sort_by=created-descending"

    @property
    def site_desc(self) -> str:
        return "Vinyleers"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = "https://vinyleers.com/a/search"
        params = {
            'type': 'product',
            'options[prefix]': 'last',
            'q': self.search_term,
            'sort_by': 'created-descending',
        }
        r = httpx.get(url=url, params=params)
        soup = BeautifulSoup(r.text, features="html.parser")
        items = soup.select('div.product-block script')
        items = [item.text.strip().lstrip('console.log("Product Object:", ').rstrip(');') for item in items]
        items = [json.loads(item) for item in items]

        for item in items:
            auction_id = str(item['id'])
            title = item['title']
            link = 'https://vinyleers.com/products/' + item['handle']
            image_link = 'https' + item['featured_image'].split('?')[0]
            _desc = '\n'.join([s for s in item['description'].splitlines() if s and s != '<p> </p>'])
            description = f"<p><strong>€{item['price'] / 100:.2f}</p></strong>\n\n{_desc}"
            start_date = datetime.datetime.fromisoformat(item['published_at'])

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                    start_date=start_date,
                )
            )
        return auctions
