from datetime import datetime
from typing import List

import httpx

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Christies(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.christies.com/en/search?entry={self.search_term}&page=1&sortby=date&tab=available_lots"

    @property
    def site_desc(self) -> str:
        return "Christies"

    def get_auctions(self) -> List[Auction]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
            'Accept': 'application/vnd.christies.v1+json',
        }

        params = {
            'keyword': self.search_term,
            'is_past_lots': False,
            'sortby': 'date',
            'language': 'en',
            'show_on_loan': 'true',
            'datasourceId': '182f8bb2-d729-4a38-b539-7cf1a901cf2e',
        }

        r = httpx.get(url='https://apim.christies.com/search-client', params=params, headers=headers)

        auctions = []

        for item in r.json()['lots']:
            auction_id = item['object_id']
            link = item['url']
            image_link = item['image']['image_src']
            _titles = [item['title_primary_txt'], item['title_secondary_txt'], item['title_tertiary_txt']]
            title = ' | '.join([x for x in _titles if x])
            start_date = datetime.fromisoformat(item['start_date'])
            end_date = datetime.fromisoformat(item['end_date'])
            description = (f"Estimate: {item['estimate_txt']}\nStart time: {start_date}\nEnd time: {end_date}\n\n"
                           f"{item['description_txt']}")

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title,
                )
            )

        return auctions
