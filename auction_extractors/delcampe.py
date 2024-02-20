from datetime import datetime

import cloudscraper as cloudscraper
from auction_extractors.base import AuctionExtractor
from bs4 import BeautifulSoup
from bs4.element import ResultSet
from models import AuctionSearchResponse, Auction


# TODO Find all auctions with sellerinfo (now isn't in the HTML from BS, maybe in cookie)


class Delcampe(AuctionExtractor):
    search_term: str
    URL: str = 'https://www.delcampe.net/en_GB/collectables/search'

    def _get_auctions(self) -> ResultSet:
        params = {'term': self.search_term}

        scraper = cloudscraper.create_scraper()

        r = scraper.get(self.URL, params=params)
        soup = BeautifulSoup(r.content, features='html.parser')
        site_auctions = soup.select('div.item-main-infos')
        return site_auctions

    def search(self) -> AuctionSearchResponse:
        auctions = []

        for auction in self._get_auctions():
            image_link = auction.select_one('a.img-view')['href']
            auction_id = auction.select_one('a.img-view')['data-item-id']
            link = f"https://www.delcampe.net{auction.select_one('a.item-link')['href']}"
            title = auction.select_one('h2.item-title').text
            _price = auction.select_one('strong.item-price').text
            _item_type = auction.select_one('div.selling-type')['title']
            desc = f'{_item_type} | {_price}'

            auctions.append(Auction(auction_id=auction_id,
                                    description=desc,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    start_date=datetime.now()
                                    ))

        return AuctionSearchResponse(
            search_link=f'https://www.delcampe.net/en_GB/collectables/search?term={self.search_term}',
            search_term=self.search_term,
            site_desc=f'Delcampe',
            auctions=auctions
        )
