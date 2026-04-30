from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class AudiophileUSA(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.audiophileusa.com/index.cfm?fuseaction=catalog.productSearchResults&searchFor=&days=&searchTerms={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "AudiophileUSA"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://www.audiophileusa.com/index.cfm'
        params = {
            'fuseaction': 'catalog.productSearchResults',
            'searchTerms': self.search_term
        }

        r = httpx.get(url=url, params=params, timeout=10.0)
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features='html.parser')

        items = soup.select('div.product-card-1')
        for item in items:
            _artist = item.select_one('span[itemprop="byArtist"]').text
            _title = item.select_one('div.product-meta').text.strip()
            title = f"{_artist} - {_title}"

            link = 'https://www.audiophileusa.com' + item.select_one('a')['href']
            image_link = 'https://www.audiophileusa.com' + item.select_one('img')['src']
            auction_id = link.split('-')[-1].replace('.html', '')

            _desc = '\n'.join([x.text.strip() for x in item.select('div.d-flex')])
            _price = item.select_one('div.product-price').text.strip()
            description = f'{_price}\n\n{_desc}'

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
