import html
import json
from typing import List

import dateparser
import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Kleinanzeigen(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.kleinanzeigen.de/s-{self.search_term}/k0'

    @property
    def site_desc(self) -> str:
        return 'Kleinanzeigen'

    def get_auctions(self) -> List[Auction]:
        r = requests.get(url=self.search_link)
        soup = BeautifulSoup(html.unescape(r.text), features='html.parser')
        items = soup.select('ul.itemlist>li.ad-listitem')

        auctions = []

        for item in items:

            try:
                auction_id = item.select_one('article')['data-adid']
            except TypeError:
                continue

            link = 'https://www.kleinanzeigen.de' + item.select_one('article')['data-href']

            try:
                image_link = item.select_one('img')['srcset'].replace('$_35', '$_59')
            except TypeError:
                image_link = 'https://www.kleinanzeigen.de/liberty/liberty-js/placeholder-logo.svg'

            try:
                title = json.loads(item.select_one('script').text)['title']
            except (TypeError, AttributeError):
                title = item.select_one('span.ellipsis').text.strip()

            try:
                _description_text = item.select_one('meta[itemprop="description"]')['content']
            except TypeError:
                _description_text = item.select_one('p.aditem-main--middle--description').text.strip()
            _price = item.select_one('p.aditem-main--middle--price-shipping--price').text.strip()
            description = f'{_description_text}\n\n{_price}'
            seller = item.select_one('div.aditem-main--top--left').text.strip()
            start_date = dateparser.parse(item.select_one('div.aditem-main--top--right').text.strip(), languages=['de'])

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link,
                    'seller': seller,
                    'start_date': start_date
                }))

        return auctions
