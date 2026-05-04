from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class HMVJapan(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.hmv.co.jp/en/search/advanced_1/category_1%2C2%2C3%2C4%2C5%2C7%2C9%2C10%2C23%2C24%2C50%2C106/formattype_1/keyword_{self.search_term}/sort_datedesc/target_ALL/'

    @property
    def site_desc(self) -> str:
        return 'HMV Japan'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'}
        s = httpx.Client(headers=headers)

        r = s.post(url=self.search_link, timeout=10.0)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features='html.parser')
        products = soup.select('ul.resultList>li.list')

        for product in products:
            _artist = product.select_one('p.name').text.strip()
            _title = product.select_one('h3.title').text.strip()
            title = f"{_artist} - {_title}"
            auction_id = product.select_one('button.js-favoritBtn')['data-sku']

            _price = product.select_one('div.price').text.strip()
            _release_date = product.select_one('div.other').text.strip()

            description = f"{_price}\n\n{_release_date}"

            link = product.select_one('h3.title>a')['href']
            image_link = product.select_one('img')['src'].replace('/190/', '/400/')

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link
                }))

        return auctions
