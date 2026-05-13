from typing import List

import dateparser
import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class DoornroosjePas(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://www.doornroosje.nl/special/doornroosjepas/"

    @property
    def site_desc(self) -> str:
        return "DoornroosjePas"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = httpx.get(self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('a.c-program__item')
        for item in items:
            link = str(item['href'])
            auction_id = link.split('/')[-2]
            description = item.select_one('div.c-program__info--subtitle').text
            _program_titles = item.select('h3.c-program__title>span')
            _program_title = ' '.join([x.text.strip() for x in _program_titles if x != ""])
            _date = dateparser.parse(' '.join([x.text for x in item.select('div.c-program__date>span')]))
            title = f'DOORNROOSJEPAS: {_date:%a %Y-%m-%d} {_program_title}'

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    link=link,
                    title=title,
                    description=description,
                )
            )

        return auctions
