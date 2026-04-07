from typing import List

import dateparser
import requests
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Kroese(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.kroese-online.nl/zoekresultaat/'

    @property
    def site_desc(self) -> str:
        return 'Kroese'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        data = {
            'what': 'artiest',
            'searchtext': self.search_term,
            'submit': 'Zoek',
        }

        r = requests.post(url=self.search_link, data=data)
        soup = BeautifulSoup(r.text, features='html.parser')
        items = soup.select('tr')
        for item in items:
            try:
                _artist = item.select_one('td.Artist').text
            except AttributeError:
                continue
            _title = item.select_one('td.Title').text
            _format = item.select_one('td.Format').text
            title = f'{_artist} - {_title} [{_format}]'
            link = 'https://www.kroese-online.nl' + item.select_one('td.Title>a')['href']
            item_id = item.select_one('td.Title')['id'].replace('Title', '')
            try:
                _release_date = dateparser.parse(item.select_one('td.Release').text).date()
            except AttributeError:
                _release_date = None
            _price = item.select_one('td.Price').text
            description = f'Format: {_format}\nRelease date: {_release_date}\nPrice: {_price}'

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': item_id,
                    'description': description,
                    'link': link
                }))

        auctions = sorted(auctions, key=lambda a: int(a.auction_id), reverse=True)
        return auctions
