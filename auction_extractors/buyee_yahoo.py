from datetime import datetime

import requests
from bs4 import BeautifulSoup

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


# TODO Translate
# TODO Multiple pages? / keep in db?


class BuyeeYahoo(AuctionExtractor):
    search_term: str

    def search(self) -> AuctionSearchResponse:
        url = f'https://buyee.jp/item/search/query/{self.search_term}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}
        page = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        auction_list = soup.find('ul', {'class': 'auctionSearchResult list_layout'})

        auctions_source = auction_list.findAll('li', {'class': 'itemCard'})
        auctions = []

        for auction in auctions_source:

            title = auction.find("div", {"class": "itemCard__itemName"}).get_text().strip()
            _url_ext = auction.find("div", {"class": "itemCard__itemName"}).find("a")["href"].split('?')[0]
            link = f"https://buyee.jp{_url_ext}"
            auction_id = _url_ext.split('/')[-1]
            _image_thumb = auction.find("div", {"class": "g-thumbnail"}).findAll("img")[1]["data-src"]
            image_link = _image_thumb.replace('wing-auctions.c.yimg.jp/sim?furl=', '').split('&')[0]
            _price_details = auction.find_all("div", {"class": "g-priceDetails"})
            _auction_price = ' '.join([x.get_text().split() for x in _price_details][0])
            _auction_days_left = auction.find("li", {"class": "itemCard__infoItem"}).find("span", {
                "class": "g-text g-text--attention"}).get_text().encode('utf-8')
            description = f'<b>{_auction_price}<br><b>Time left:</b> {_auction_days_left}<br>'

            auctions.append(Auction(title=title,
                                    auction_id=auction_id,
                                    description=description,
                                    link=link,
                                    image_link=image_link,
                                    start_date=datetime.now()))

        return AuctionSearchResponse(search_link=page.url,
                                     search_term=self.search_term,
                                     site_desc='Buyee (Yahoo)',
                                     auctions=auctions)


if __name__ == '__main__':
    bm = BuyeeYahoo(search_term='(デビッド・ボウイ bowie) -シャツ -dvd -cd-r -cdr')
    result = bm.search()
    print(result)
