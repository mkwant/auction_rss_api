import json
from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class PlatomaniaExclusives(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.platomania.nl/concerto-exclusives'

    @property
    def site_desc(self) -> str:
        return 'Platomania Exclusives'

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url=self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('article.article')

        auctions = []
        for item in items:
            item_info = json.loads(str(item.select_one('a.bestel')['data-article-data']))

            item_id = str(item.select_one('a.bestel')['data-article-id'])
            title = f"{item_info['artist']} - {item_info['title']}"
            link = f"https://www.platomania.nl/article/{item_id}"
            image_link = 'https://www.platomania.nl' + str(item.select_one('img')['src'])
            _price = item_info['price']
            _details = '\n'.join([x.text.strip() for x in item.select('div.article-details__text')])
            description = f"Prijs: Eur {_price}\n{_details}"

            auctions.append(
                Auction(
                    auction_id=item_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
