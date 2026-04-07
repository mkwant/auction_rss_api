from typing import List

import requests

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class Sothebys(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.sothebys.com/en/search?query={self.search_term}&tab=objects&sortBy=bsp_dotcom_prod_en_ending_soonest'

    @property
    def site_desc(self) -> str:
        return 'Sothebys'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        data = f'{{"requests":[{{"indexName":"bsp_dotcom_prod_en_ending_soonest","params":"highlightPreTag=clickAnalytics=true&hitsPerPage=51&filters=type%3A%22Bid%22%20OR%20type%3A%22Buy%20Now%22%20OR%20type%3A%22Lot%22%20OR%20type%3A%22Private%20Sale%22%20OR%20type%3A%22Retail%22&query={self.search_term}&maxValuesPerFacet=9999&page=0&facets=%5B%22type%22%2C%22endDate%22%2C%22lowEstimate%22%2C%22highEstimate%22%2C%22artists%22%2C%22departments%22%5D&tagFilters="}}]}}'

        r = requests.post(
            url='https://o28sy4q7wu-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.2.0)%3B%20Browser%20(lite)%3B%20react%20(16.13.1)%3B%20react-instantsearch%20(6.7.0)%3B%20JS%20Helper%20(3.2.2)&x-algolia-api-key=e732e65c70ebf8b51d4e2f922b536496&x-algolia-application-id=O28SY4Q7WU',
            data=data,
        )

        items = r.json()['results'][0]['hits']
        for item in items:
            auction_id = item['objectID']
            title = item['title']
            try:
                _desc = item['fullText']
            except KeyError:
                _desc = item['description']
            description = f'{item['type']}, {item['details']}\n\n{_desc}'
            link = item['url']
            image_link = item['image']

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
