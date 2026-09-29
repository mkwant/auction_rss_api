from pathlib import Path
from typing import List

import dateparser
import httpx2
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

        r = httpx2.get(self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        items = soup.select('a.c-program__item')

        last_date = None  # items without their own date inherit the previous item's date
        for item in items:
            link = str(item['href'])
            auction_id = link.split('/')[-2]
            description = item.select_one('div.c-program__info--subtitle').text

            _program_titles = item.select('h3.c-program__title>span')
            _program_title = ' '.join(
                t for t in (x.text.strip() for x in _program_titles) if t
            )

            _date_text = ' '.join(x.text.strip() for x in item.select('div.c-program__date>span')).strip()
            _date = dateparser.parse(_date_text) if _date_text else None

            if _date is not None:
                last_date = _date
            else:
                _date = last_date  # same day as the previous entry

            date_str = f'{_date:%a %Y-%m-%d}' if _date else 'date unknown'
            title = f'DOORNROOSJEPAS: {date_str} {_program_title}'

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    link=link,
                    title=title,
                    description=description,
                )
            )

        return auctions
