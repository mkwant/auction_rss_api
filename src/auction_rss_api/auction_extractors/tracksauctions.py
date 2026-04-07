import hashlib
from typing import List

import requests
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class TracksAuctions(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://bid.tracksauctions.com/auction/search/?st=bowie&g=-1'

    @property
    def site_desc(self) -> str:
        return 'Tracks Auctions'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = requests.get(self.search_link)
        soup = BeautifulSoup(r.content, features='html.parser')
        items = soup.select('div.auction-lot')

        for item in items:
            title = item.select_one('span.lot-title').text.strip()
            link = 'https://bid.tracksauctions.com' + item.select_one('p.auction-lot-title>a')['href']
            image_link = item.select_one('div.auction-lot-image img')['src'].replace('-small', '')
            auction_id = hashlib.md5(link.encode('utf-8')).hexdigest()

            _auction_info = item.select('p.auction-lot-title')[1].text.strip().split('(')[1].split(')')[0]

            try:
                _estimate = item.select_one('div.estimate').text.strip()
            except AttributeError:
                _estimate = ''

            _desc = item.select_one('p.lot-desc').text.replace('... read more', '').strip() + ' ...'
            description = f'{_auction_info}\n{_estimate}\n\n{_desc}'

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
