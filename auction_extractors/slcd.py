from typing import List

import requests
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class SLCD(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://slcd.com/cgi-bin/mysqlShop.cgi?cPage=PreSearch&cGroup=New+In+Stock&cAction={self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'SLCD'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        r = requests.get(url=self.search_link)
        soup = BeautifulSoup(r.text, 'html.parser')
        tables = soup.select('table')
        item_table = tables[4]
        items = item_table.select('tr>td')

        for item in items:
            link = 'https://slcd.com' + item.select_one('a')['href']
            auction_id = link.split('=')[-1]
            image_link = 'https://slcd.com' + item.select_one('img')['src'].replace('_sm', '')
            description = item.select_one('p').getText(separator='').replace(' Buy', '')
            title = ' - '.join(description.split('\n')[0:2])

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title
                )
            )

        return auctions
