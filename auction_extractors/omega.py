from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Omega(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return (f'https://bid.omegaauctions.co.uk/auction/search/?g=1&st={self.search_term}'
                f'&sto=0&sf=%5B%5D&w=False&pp=96&so=4&pn=1')

    @property
    def site_desc(self) -> str:
        return "Omega Auctions"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = requests.get(self.search_link)
        soup = BeautifulSoup(r.text, features='html.parser')

        items = soup.select('div.auction-grid-lot')
        for item in items:

            auction_id = item.select_one('a.anchor-offset')['name']
            link = 'https://bid.omegaauctions.co.uk' + item.select_one('div.auction-lot')['data-detailsurl']
            image_link = item.select_one('img')['src'].replace('-small.', '-medium.')
            title = item.select_one('span.lot-title').text.strip()

            _estimate = item.select_one('div.estimate').text.strip()
            try:
                _premium = item.select_one('div.estimate>span')['title']
            except TypeError:
                _premium = item.select_one('div.clearfix')['title']

            try:
                _current = (f"{item.select_one('span.tb-heading').text.strip()} "
                            f"{item.select_one('span.tb-nobid').text.strip()}")
            except AttributeError:
                _current = ''
            description = f"{_estimate}\n{_premium}\n\n{_current}".strip()

            try:
                _ended = item.select_one('span.timed-ended').text.strip()
                description = f"{_ended}\n\n{description}"
            except AttributeError:
                pass

            auctions.append(
                Auction(auction_id=auction_id,
                        description=description,
                        image_link=image_link,
                        link=link,
                        title=title,
                        start_date=datetime.now()
                        )
            )

        return auctions
