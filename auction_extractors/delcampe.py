from datetime import datetime

import cloudscraper as cloudscraper
from auction_extractors.base import AuctionExtractor
from bs4 import BeautifulSoup, ResultSet
from models import AuctionSearchResponse, Auction


# TODO Find all auctions with sellerinfo (now isn't in the HTML from BS, maybe in cookie)


class Delcampe(AuctionExtractor):
    search_term: str
    URL = 'https://www.delcampe.net/en_GB/collectables/search'

    def _get_auctions(self) -> ResultSet:
        params = {'term': self.search_term}

        scraper = cloudscraper.create_scraper()

        r = scraper.get(self.URL, params=params)
        soup = BeautifulSoup(r.content, 'html.parser')
        site_auctions = soup.find_all('div', {'class': 'item-main-infos'})
        return site_auctions

    def search(self) -> AuctionSearchResponse:

        auctions = []

        for auction in self._get_auctions():
            image_link = auction.find('a', {'class': 'img-view'})['href']
            auction_id = auction.find('a', {'class': 'img-view'})['data-item-id']
            link = f"https://www.delcampe.net{auction.find('a', {'class': 'item-link'})['href']}"
            title = auction.find('h2', {'class': 'item-title font-md font-normal'}).text
            _price = auction.find('strong', {'class': 'item-price font-xl'}).text
            _item_type = auction.find('div', {'class': 'selling-type'})['title']
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
