import hashlib
from datetime import datetime
from typing import List

import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class LuxorLive(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.luxorlive.nl/?pagina=1'

    @property
    def site_desc(self) -> str:
        return "LuxorLive"

    def get_auctions(self) -> List[Auction]:
        r = httpx2.get(url=self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')

        auctions = []

        events = soup.select('div.agenda>div.item')
        for event in events:
            _start_date = datetime.fromisoformat(str(event.select_one("meta[itemprop='startDate']")['content']))
            _title = event.select_one('div.title>h3.big').text.strip()
            title = f"{_start_date:%a %Y-%m-%d}: {_title}"

            link = str(event.select_one('a')['href'])
            image_link = event.select_one('img')['data-src'].replace('-320x200', '-1920x630')

            unique_id = hashlib.md5(image_link.encode()).hexdigest()

            _subtitle = event.select_one('div.title>div.subtitle').text.strip()
            _desc = event.select_one("meta[itemprop='description']")['content']
            description = f"{_subtitle}\n\n{_desc}"

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
