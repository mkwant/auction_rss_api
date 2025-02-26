from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class CdAndLp(AuctionExtractor):
    search_term: str
    URL: str = 'https://www.cdandlp.com/en/search/'

    @property
    def site_desc(self) -> str:
        return 'CDandLP'

    @property
    def search_link(self) -> str:
        return f'{self.URL}?q={self.search_term}&srt=2'

    @staticmethod
    def strike(text):
        result = ''
        for char in text:
            result = result + char + '\u0336'
        return result

    def _get_auctions(self) -> ResultSet:
        params = {'q': self.search_term,
                  'srt': 2}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}
        s = requests.Session()

        # Retrieve cookies
        s.get(url='https://www.cdandlp.com')
        r = s.get(url=self.URL, params=params, headers=headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.content, features='html.parser')
        site_auctions = soup.select('div[class*="twelve large-20 columns div_item_listing"]')
        return site_auctions

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for auction in self._get_auctions():

            link = auction.find('a')['href']
            auction_id = link.split('/')[-2]

            title = auction.find('a', {'class': 'listingTitle textColor12 capitalize'}).get_text(separator=': ',
                                                                                                 strip=True)
            image_link = auction.find('img').get('data-src')

            _seller = auction.find('div', {'class': 'one large-20 medium-20 columns listingSeller show-for-medium-up'})
            _seller_name = _seller.find('a').text
            _seller_cty = _seller.find('span').text
            seller = f'{_seller_name} {_seller_cty}'

            try:
                _price = auction.find('span', {'class': 'listingPrice1'}).text.strip()
            except AttributeError:
                _price_strike = auction.find('span', {'class': 'listingPriceCrossed'}).text.strip()
                _price_discount = auction.find('span', {'class': 'listingPriceDiscount'}).text.strip()
                _price = f'{self.strike(_price_strike)}  {_price_discount}'

            try:
                _condition = auction.find('span', {'class': 'has-tip tip-bottom has-tip-listing'}).text.strip()
            except AttributeError:
                _condition = auction.find(
                    'div', {'class': 'one large-6 medium-20 columns listingGrading show-for-medium-up'}).text.strip()

            _format = auction.find(
                'div',
                {'class': 'one large-6 medium-20 columns listingMedia_responsive show-for-medium-up'}).text.strip()

            try:
                _cat_no = auction.find('span', {'class': 'listingCar textColor2'}).text.strip()
            except AttributeError:
                _cat_no = ''
            desc = f'{_price} | {_condition} | {_format} | {_cat_no}'

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=desc,
                    image_link=image_link,
                    link=link,
                    title=title,
                    seller=seller
                )
            )

        return auctions

if __name__ == '__main__':
    c = CdAndLp(search_term='bowie')
    auctions = c.get_auctions()
    print(auctions)