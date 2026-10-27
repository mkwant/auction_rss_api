import hashlib
import datetime
from typing import List

import dateparser
import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class DavidBowieNews(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://www.davidbowie.com/news"

    @property
    def site_desc(self) -> str:
        return "David Bowie Official News"

    def get_auctions(self) -> List[Auction]:
        r = httpx2.get(url=self.search_link, timeout=10.0)
        r.raise_for_status()

        auctions = []

        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('div.summary-item')
        for item in items:
            title = item.select_one('div.summary-title').text.strip()
            _slug = str(item.select_one('a')['href'])
            unique_id = hashlib.md5(_slug.encode()).hexdigest()
            link = f'https://www.davidbowie.com{_slug}'
            image_link = str(item.select_one('img')['data-image'])

            try:
                published_date = dateparser.parse(str(item.select_one('time')['datetime']))
            except TypeError:
                year, month, date = _slug.split('/')[2:5]
                published_date = datetime.date(year=int(year), month=int(month), day=int(date))

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    start_date=published_date,
                    description="",
                )
            )

        return auctions
