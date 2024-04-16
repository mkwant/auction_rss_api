import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from app.models import AuctionExtractor, Auction


class MusicStack(AuctionExtractor):
    search_term: str

    @property
    def search_link(self) -> str:
        return f'https://www.musicstack.com/show.cgi?per_page=50&new=1&find={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'MusicStack'

    def get_auctions(self) -> List[Auction]:
        url = 'https://www.musicstack.com/show.cgi'
        params = {
            'per_page': 50,
            'find': self.search_term,
            'new': 1
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}

        r = requests.get(url=url, params=params, headers=headers)
        soup = BeautifulSoup(r.text, features='html.parser')

        table = soup.find(name='table', attrs={'border': 0, 'cellpadding': 3, 'cellspacing': 0, 'width': '100%'})
        rows = table.select('tr')

        auctions = []

        for row in rows[1:]:
            link = row.select_one('a.nd')['href']

            # Skip header for items with multiple listings
            if 'show.cgi' in link:
                continue

            try:
                image_link = row.select_one('img')['big_image']
            except KeyError:
                image_link = ''
            auction_id = link.split('/')[-1]
            title = row.select_one('a').text

            cells = row.select('td')

            _description = cells[4].text.strip()
            _format = cells[6].text.strip()
            _condition = cells[7].text.strip()
            _price = cells[10].text.strip()
            description = '\n'.join((_price, _format, _condition, _description))
            author = cells[8].get_text(separator=', ')
            link = cells[12].select_one('a.t')['href']
            days_ago = cells[9].text.split()[0]
            start_date = datetime.date.today() - datetime.timedelta(days=int(days_ago))

            auctions.append(
                Auction(
                    title=title,
                    auction_id=auction_id,
                    description=description,
                    link=link,
                    image_link=image_link,
                    author=author,
                    start_date=start_date
                )
            )
        return auctions
