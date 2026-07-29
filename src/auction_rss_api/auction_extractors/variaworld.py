from datetime import datetime
from typing import List
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Variaworld(AuctionExtractor):
    search_term: str

    @property
    def site_desc(self) -> str:
        return 'Variaworld'

    @property
    def search_link(self) -> str:
        return (f'https://www.variaworld.nl/alles/m_ge=[j;m;u]&ts=1&zoek={self.search_term}'
                f'&zoek_at=a&m_sr=lig&startpagina=1')

    def _get_auctions(self) -> ResultSet:
        r = httpx.get(self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.content, features='html.parser')

        site_auctions = soup.select('a.overzichtbox_2')
        return site_auctions

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for auction in self._get_auctions():
            link = 'https://www.variaworld.nl' + auction['href']
            auction_id = str(parse_qs(urlparse(link).query)['at'][0])
            image = auction.select_one('div.overzichtfotobox_2')
            image_link = f"https://www.variaworld.nl{image.select_one('img')['src']}"

            _artist_name = auction.select_one('div.koptekst').text.strip()
            _item_name, _item_type = auction.select('div.tekst')
            _item_name = _item_name.text.strip()
            _item_type = _item_type.text.strip()
            _item_price = auction.select_one('span[class^="div_kleur_prijs_"]').text.strip()

            title = f"{_artist_name} - '{_item_name}' ({_item_type})"
            description = '\n'.join([_artist_name, _item_name, _item_type, _item_price])
            start_date = auction.select_one('div.overzicht_datum_ingebracht').text.strip().split('\n')[0]
            start_date = datetime.strptime(start_date, '%d-%m-%Y')

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title,
                    start_date=start_date
                )
            )

        return auctions
