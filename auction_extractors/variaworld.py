from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class Variaworld(AuctionExtractor):
    search_term: str

    def _get_auctions(self) -> ResultSet:
        URL = f'https://www.variaworld.nl/alles/m_ge=[j;m;u]&ts=1&zoek={self.search_term}&zoek_at=a&m_sr=lig&startpagina=1'  # noqa
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'html.parser')

        site_auctions = soup.find_all('a', {'class': 'overzichtbox_2'})
        return site_auctions

    def search(self) -> AuctionSearchResponse:
        auctions = []

        for auction in self._get_auctions():
            link = auction['href']
            auction_id = link.split('&at=')[1].split('&')[0]
            image = auction.find('div', {'class': 'overzichtfotobox_2'})
            image_link = f"https://www.variaworld.nl{image.find('img')['src']}"
            _artist_name = auction.find('div', {'class': 'koptekst'}).text.strip()
            _item_name, _item_type = auction.find_all('div', {'class': 'tekst'})
            _item_name = _item_name.text.strip()
            _item_type = _item_type.text.strip()
            try:
                _item_price = auction.find('span', {'class': 'div_kleur_prijs_1'}).text.strip()
            except AttributeError:
                _item_price = auction.find('span', {'class': 'div_kleur_prijs_2'}).text.strip()
            title = f"{_artist_name} - '{_item_name}' ({_item_type})"
            description = '\n'.join([_artist_name, _item_name, _item_type, _item_price])
            start_date = auction.find('div', {'class', 'overzicht_datum_ingebracht'}).text.strip()
            start_date = datetime.strptime(start_date, '%d-%m-%Y')

            auctions.append(Auction(auction_id=auction_id,
                                    description=description,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    start_date=start_date
                                    ))

        return AuctionSearchResponse(
            search_link=f'https://www.variaworld.nl/alles/m_ge=[j;m;u]&ts=1&zoek={self.search_term}&zoek_at=a&m_sr=lig&startpagina=1',  # noqa
            search_term=self.search_term,
            site_desc=f'Variaworld',
            auctions=auctions
        )
