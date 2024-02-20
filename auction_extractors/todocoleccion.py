from datetime import datetime

import cloudscraper as cloudscraper
from auction_extractors.base import AuctionExtractor
from bs4 import BeautifulSoup
from bs4.element import  ResultSet
from models import AuctionSearchResponse, Auction


class Todocoleccion(AuctionExtractor):
    search_term: str
    URL: str = 'https://en.todocoleccion.net/buscador'

    def _get_auctions(self, search_term: str) -> ResultSet:
        params = {'from': 'top',
                  'bu': search_term}

        scraper = cloudscraper.create_scraper()

        r = scraper.get(self.URL, params=params)
        soup = BeautifulSoup(r.content, features='html.parser')
        site_auctions = soup.select('div._lote_item-image-and-content')
        return site_auctions

    def search(self) -> AuctionSearchResponse:

        auctions = []

        for auction in self._get_auctions(search_term=self.search_term):
            image_link = auction.select_one('img')['src'].split('?')[0]

            _item_info = auction.select_one('a.js-lot-titles')
            title = _item_info.text.strip()
            link = 'https://en.todocoleccion.net' + _item_info['href']
            unique_id = _item_info['id'].replace('lot-title-', '')
            price = auction.select_one('span.precio-lote-listado').text

            _seller_block = auction.select_one('p.lote-vendedor')
            if _seller_block is not None:
                seller = _seller_block.select_one('span').text.strip()
            else:
                seller = ''

            _item_type_block = auction.select_one('a._lote_item-img-footerbox')
            if _item_type_block is not None:
                _item_type = _item_type_block.text.strip()
            else:
                _item_type = 'Buy now'
            _category = auction.select_one('p._lote_item-section').text.strip()
            desc = f'{price} | {_item_type} | {_category}'

            auctions.append(Auction(auction_id=unique_id,
                                    description=desc,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    seller=seller,
                                    start_date=datetime.now()
                                    ))

        return AuctionSearchResponse(
            search_link=f'https://en.todocoleccion.net/buscador?from=top&bu={self.search_term}',
            search_term=self.search_term,
            site_desc=f'Todocoleccion',
            auctions=auctions
        )
