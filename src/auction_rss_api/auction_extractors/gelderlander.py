import hashlib
import json
from typing import List
from urllib.parse import quote

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Gelderlander(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.gelderlander.nl/{self.search_term}/'

    @property
    def site_desc(self) -> str:
        return "Gelderlander"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url=self.search_link)
        r.raise_for_status()

        auctions = []

        soup = BeautifulSoup(markup=r.text, features='html.parser')
        json_str = soup.select_one('script[type="application/ld+json"]').text
        json_parsed = json.loads(json_str)
        items = json_parsed['@graph'][1]['itemListElement']
        for item in items:
            item = item['item']

            unique_id = hashlib.md5(item['url'].encode()).hexdigest()
            title = item['name']

            if item['isAccessibleForFree'] == 'True':
                link = item['url']
            else:
                link = f"https://archive.is/?run=1&url={quote(item['url'], safe='')}"

            image_link = item['image'][0]['url']
            author = item['author'][0]['name']
            date_published = dateparser.parse(item['datePublished'])

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description='',
                    seller=author,
                    start_date=date_published,
                )
            )

        return auctions
