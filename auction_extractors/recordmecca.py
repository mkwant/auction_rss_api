from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class RecordMecca(AuctionExtractor):
    search_term: str

    def _get_auctions(self) -> ResultSet:
        url = 'https://recordmecca.com'
        params = {'s': self.search_term}

        r = requests.get(url=url, params=params)
        soup = BeautifulSoup(r.content, 'html.parser')
        items = soup.select('div.default_product_display')
        return items

    def search(self) -> AuctionSearchResponse:
        auctions = []

        for item in self._get_auctions():
            title = item.select_one('h2').get_text(strip=True)
            link = item.select_one('a')['href']
            image_link = item.select_one('img.featured_list_image')['src'].split('?')[0]
            _desc = item.select_one('div.wpsc_description').get_text(strip=True)
            _price = item.select_one('span.currentprice').get_text(strip=True)
            description = '\n'.join([_price, _desc])
            auction_id = link.split('/')[-2]

            auctions.append(Auction(auction_id=auction_id,
                                    description=description,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    start_date=datetime.now()
                                    ))

        return AuctionSearchResponse(
            search_link=f'https://recordmecca.com?s={self.search_term}',
            search_term=self.search_term,
            site_desc=f'RecordMecca',
            auctions=auctions
        )
