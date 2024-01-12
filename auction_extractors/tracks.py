from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class Tracks(AuctionExtractor):
    search_term: str

    def _get_auctions(self) -> ResultSet:
        self.search_term = self.search_term.lower().replace(' ', '-')
        url = f"https://www.tracks.co.uk/category/various-artists-memorabilia/{self.search_term}"

        r = requests.get(url=url)
        soup = BeautifulSoup(r.content, 'html.parser')
        items = soup.select('ul.products li')
        return items

    def search(self) -> AuctionSearchResponse:
        auctions = []

        for item in self._get_auctions():
            title = item.select_one('h2').get_text()
            _desc = item.select_one('div.woo-short-description').get_text(strip=True)
            image_link = item.select_one('img')['src']
            link = item.select_one('a.un-loop-thumbnail')['href']
            auction_id = link.split('/')[4].split('-')[0]
            _price = item.select_one('span.price').get_text()
            description = '\n'.join([_price, _desc])

            auctions.append(Auction(auction_id=auction_id,
                                    description=description,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    start_date=datetime.now()
                                    ))

        return AuctionSearchResponse(
            search_link=f'https://www.tracks.co.uk/category/various-artists-memorabilia/{self.search_term}',
            search_term=self.search_term,
            site_desc=f'Tracks.co.uk',
            auctions=auctions
        )


if __name__ == '__main__':
    t = Tracks(search_term='david bowie')
    print(t.search())
