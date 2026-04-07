from typing import List

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class LastDodo(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.lastdodo.nl/nl/marketplace/search?q={self.search_term}&sort_by=created_at'

    @property
    def site_desc(self) -> str:
        return 'LastDodo'

    def get_auctions(self) -> List[Auction]:
        auctions = []
        response = httpx.get(url=self.search_link)
        soup = BeautifulSoup(response.text, features='html.parser')

        items = soup.select('div.card-item')
        for item in items:
            link = item.select_one('a')['href']

            # Skip featured auctions
            if link.endswith('?referer=marketplace'):
                continue

            try:
                image_link = item.select_one('picture>source')['data-srcset'].replace('ld_thumb3_webp', 'ld_large')
            except TypeError:
                image_link = None
            auction_id = link.split('?')[0].split('/')[-1]
            _title = item.select_one('div.title').text
            _serie = item.select_one('div.serie').text
            title = f'{_serie} - {_title}'

            _edition = ' / '.join([x.text for x in item.select('div.edition>ul>li')])
            _badge = item.select_one('div.state').text

            try:
                _notes = item.select_one('div.notes').text
            except AttributeError:
                _notes = ''
            _price = item.select_one('div.wrap-price').text.replace(' ', '')
            _seller = item.select_one('div.user-name').text
            _review = item.select_one('div.review').text
            since = dateparser.parse(item.select_one('ul.text-muted>li').text.strip().replace('Aangeboden op ', ''))
            seller = f'{_seller} {_review}'
            desc = f'{_price} / {_badge}\n{_edition}\n\n{_notes}'.strip()

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=desc,
                    seller=seller,
                    start_date=since
                )
            )

        return auctions
