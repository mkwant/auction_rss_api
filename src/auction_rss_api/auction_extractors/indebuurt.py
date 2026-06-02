import hashlib
import json
import time
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

    def fetch_page(self) -> httpx.Response:
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                r = httpx.get(url=self.search_link, timeout=3.0)

                if r.status_code == 503:
                    raise httpx.HTTPStatusError(
                        message="503 Service Unavailable",
                        request=r.request,
                        response=r,
                    )

                return r

            except (httpx.TimeoutException, httpx.HTTPStatusError):
                if attempt == max_attempts - 1:
                    raise

                print('retrying')
                time.sleep(0.5)

        raise AssertionError("Unreachable")

    def get_auctions(self) -> List[Auction]:
        r = self.fetch_page()
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

        auctions = sorted(auctions, key=lambda auction: auction.start_date, reverse=True)
        return auctions
