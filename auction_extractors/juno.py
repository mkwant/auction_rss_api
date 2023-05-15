from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class Juno(AuctionExtractor):
    search_term: str

    def _get_auctions(self) -> ResultSet:
        url = 'https://www.juno.co.uk/search/'
        params = {'q[all][0]': self.search_term,
                  'hide_forthcoming': 0,
                  'solrorder': 'date_down'}

        r = requests.get(url=url, params=params)
        page = r.text

        soup = BeautifulSoup(page, 'html.parser')
        product_list = soup.find('div', {'class': 'product-list'})
        items = product_list.find_all('div', {'class': 'dv-item'})
        return items

    def search(self) -> AuctionSearchResponse:
        auctions = []

        for item in self._get_auctions():
            item_id = item['id'].split("-")[1]
            try:
                _forthcoming = item.find('div',
                                         {'class': 'tag-status tag-status-stretch'}).text.strip() == 'FORTHCOMING'
            except AttributeError:
                _forthcoming = False
            link = 'https://www.juno.co.uk' + item.find('a')['href']
            image_link = f'https://imagescdn.juno.co.uk/full/CS{item_id}-01A-BIG.jpg'
            _artist, _title, _label, _cat = [x.text for x in item.find_all('div', {'class': 'vi-text mb-1'})]
            _price = item.find('div', {'class': 'pl-big-price'}).text.strip()
            title = f'{_artist} - {_title}'
            if _forthcoming:
                title = f'[Pre-order] {title}'
            description = f'{_price}\n{_label}\n{_cat}'

            auctions.append(Auction(auction_id=item_id,
                                    description=description,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    start_date=datetime.now()
                                    ))

        return AuctionSearchResponse(
            search_link=f'https://www.juno.co.uk/search/?q%5Ball%5D%5B0%5D={self.search_term}&'
                        f'hide_forthcoming=0&solrorder=date_down',
            search_term=self.search_term,
            site_desc=f'Juno',
            auctions=auctions
        )
