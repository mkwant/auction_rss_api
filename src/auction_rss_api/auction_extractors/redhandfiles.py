import hashlib
import json
from datetime import datetime
from typing import List

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class RedHandFiles(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://www.theredhandfiles.com/"

    @property
    def site_desc(self) -> str:
        return "The Red Hand Files"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = httpx.get(self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        json_str = soup.select_one('script[type="application/ld+json"]').text
        json_parsed = json.loads(json_str)
        self.feed_description = json_parsed['description']
        posts = json_parsed['blogPost']
        for post in posts:
            title = post['headline'].strip()
            link = post['url']
            unique_id = hashlib.md5(link.encode()).hexdigest()
            image_link = post['image']['url']
            description = post['description']
            author = post['author']['name']
            created_at = dateparser.parse(post['datePublished']) or datetime.now()

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                    seller=author,
                    start_date=created_at,
                )
            )

        return auctions
