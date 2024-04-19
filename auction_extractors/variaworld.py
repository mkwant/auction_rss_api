from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from models.auctionextractor import AuctionExtractor
from models.auction import Auction


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
        url = (f'https://www.variaworld.nl/alles/m_ge=[j;m;u]&ts=1&zoek={self.search_term}'
               f'&zoek_at=a&m_sr=lig&startpagina=1')
        r = requests.get(url)
        soup = BeautifulSoup(r.content, features='html.parser')

        site_auctions = soup.select('a.overzichtbox_2')
        return site_auctions

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for auction in self._get_auctions():
            link = auction['href']
            auction_id = link.split('&at=')[1].split('&')[0]
            image = auction.select_one('div.overzichtfotobox_2')
            image_link = f"https://www.variaworld.nl{image.select_one('img')['src']}"
            _artist_name = auction.select_one('div.koptekst').text.strip()
            _item_name, _item_type = auction.select('div.tekst')
            _item_name = _item_name.text.strip()
            _item_type = _item_type.text.strip()
            try:
                _item_price = auction.select_one('span.div_kleur_prijs_1').text.strip()
            except AttributeError:
                _item_price = auction.select_one('span.div_kleur_prijs_2').text.strip()
            title = f"{_artist_name} - '{_item_name}' ({_item_type})"
            description = '\n'.join([_artist_name, _item_name, _item_type, _item_price])
            start_date = auction.select_one('div.overzicht_datum_ingebracht').text.strip()
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
