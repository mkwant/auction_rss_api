from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class PleasuresOfPastTimes(AuctionExtractor):
    search_term: str

    def _get_auctions(self) -> ResultSet:
        self.search_term = self.search_term.replace(' ', '-')
        url = f'https://pleasuresofpasttimes.com/shop/product-category/memorabilia/{self.search_term}/?orderby=date'

        r = requests.get(url=url)
        soup = BeautifulSoup(r.content, 'html.parser')
        items = soup.select('ul.products li')
        return items

    def search(self) -> AuctionSearchResponse:
        auctions = []

        for item in self._get_auctions():
            title = item.select_one('h2').get_text()
            _desc = item.select_one('span.loop-long-desc').get_text(strip=True)
            image_link = item.select_one('img')['src']
            link = item.select_one('a.button')['href']
            auction_id = link.split('/')[-2]
            try:
                _price = item.select_one('span.price').get_text()
            except AttributeError:
                _price = '-'
            description = '\n'.join([_price, _desc])

            auctions.append(Auction(auction_id=auction_id,
                                    description=description,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    start_date=datetime.now()
                                    ))

        return AuctionSearchResponse(
            search_link=f'https://pleasuresofpasttimes.com/shop/product-category/memorabilia/{self.search_term}/?orderby=date',  # noqa
            search_term=self.search_term,
            site_desc=f'Pleasures Of Past Times',
            auctions=auctions
        )
