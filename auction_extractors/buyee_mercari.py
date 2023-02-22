from datetime import datetime

import requests
from bs4 import BeautifulSoup

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction

# TODO Add if sold: <div class="soldOut__text">SOLD</div>
# TODO Translate


class BuyeeMercari(AuctionExtractor):
    search_term: str

    def search(self) -> AuctionSearchResponse:
        url = 'https://buyee.jp/mercari/search'
        params = {'keyword': self.search_term, 'status': 'all'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}
        page = requests.get(url=url, params=params, headers=headers)

        soup = BeautifulSoup(page.content, 'html.parser')
        auction_list = soup.find('ul', {'class': 'item-lists'})
        auctions_source = auction_list.findAll('li', {'class': 'list'})
        auctions = []

        for auction in auctions_source:
            title = auction.find('h2', {'class': 'name'}).text
            link = f"https://buyee.jp{auction.find('a')['href'].split('?')[0]}"
            auction_id = link.split('/')[-1]
            image_link = f"https://static.mercdn.net/item/detail/orig/photos/{auction_id}_1.jpg"
            _price_yen = auction.find('p', {'class': 'price'}).text
            _price_eur = auction.find('p', {'class': 'price-fx'}).text
            description = f'{_price_yen} {_price_eur}'

            auctions.append(Auction(title=title,
                                    auction_id=auction_id,
                                    description=description,
                                    link=link,
                                    image_link=image_link,
                                    start_date=datetime.now()))

        return AuctionSearchResponse(search_link=page.url,
                                     search_term=self.search_term,
                                     site_desc='Buyee (Mercari)',
                                     auctions=auctions)
