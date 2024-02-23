from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import Auction


class Juno(AuctionExtractor):
    search_term: str

    @property
    def site_desc(self) -> str:
        return 'Juno'

    @property
    def search_link(self) -> str:
        return f'https://www.juno.co.uk/search/?q%5Ball%5D%5B0%5D={self.search_term}' \
               f'&hide_forthcoming=0&solrorder=date_down'

    def _get_auctions(self) -> ResultSet:
        url = 'https://www.juno.co.uk/search/'
        params = {
            'q[all][0]': self.search_term,
            'hide_forthcoming': 0,
            'solrorder': 'date_down'
        }

        r = requests.get(url=url, params=params)
        page = r.text

        soup = BeautifulSoup(page, features='html.parser')
        items = soup.select('div.product-list>div.dv-item')
        return items

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in self._get_auctions():
            item_id = item['id'].split("-")[1]
            try:
                _forthcoming = item.select_one('div.tag-status').text.strip() == 'FORTHCOMING'
            except AttributeError:
                _forthcoming = False
            link = 'https://www.juno.co.uk' + item.select_one('a')['href']
            image_link = f'https://imagescdn.juno.co.uk/full/CS{item_id}-01A-BIG.jpg'

            _artist, _title, _label, _cat, *_ = [x.text for x in item.select('div.vi-text')]
            _cat = _cat.replace(' Add to playlist', '')
            _price = item.select_one('div.pl-big-price').text.strip()
            title = f'{_artist} - {_title}'
            if _forthcoming:
                title = f'[Pre-order] {title}'
            description = f'{_price}\n{_label}\n{_cat}'

            auctions.append(
                Auction(
                    auction_id=item_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title,
                    start_date=datetime.now()
                )
            )

        return auctions
