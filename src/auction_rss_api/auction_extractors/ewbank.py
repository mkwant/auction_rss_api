from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Ewbank(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.ewbankauctions.co.uk/catalog?query={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "Ewbank Auctions"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.ewbankauctions.co.uk/catalog'
        params = {'query': self.search_term}
        r = httpx.get(url, params=params)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, features='html.parser')
        items = soup.select('div.com_catalog__lot-box')
        for item in items:
            auction_id = item['id']
            link = item.select_one('a.full-details-link')['href']
            image_link = item.select_one('img')['src'].replace('medium', 'xlarge')
            title = item.select_one('h2.lot-name').text.strip()
            description = '\n'.join(
                [x.strip() for x in item.select_one('div.wrapper').text.strip().split('\n') if x != ''])

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                )
            )

        return auctions
