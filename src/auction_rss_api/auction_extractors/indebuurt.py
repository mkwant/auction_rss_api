import hashlib
import json
from typing import List

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class InDeBuurt(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://indebuurt.nl/{self.search_term}/nieuws/"

    @property
    def site_desc(self) -> str:
        return "InDeBuurt"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url=self.search_link)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features="html.parser")
        json_str = soup.select_one('script[type="application/ld+json"]')
        json_parsed = json.loads(json_str.text)
        items = json_parsed['@graph'][1]['itemListElement']

        auctions = []

        for item in items:
            item = item['item']

            auction_id = hashlib.md5(item['name'].encode()).hexdigest()
            title = item['name']
            description = item['headline']
            link = item['url']
            image_link = item['image'][0]['url']

            try:
                author = item['author'][0]['name']
            except KeyError:
                author = None

            publish_date = dateparser.parse(item['datePublished'])

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    description=description,
                    link=link,
                    image_link=image_link,
                    seller=author,
                    start_date=publish_date,
                )
            )

        return auctions
