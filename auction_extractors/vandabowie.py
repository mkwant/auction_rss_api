from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class VandaBowie(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return 'https://www.vam.ac.uk/shop/david-bowie'

    @property
    def site_desc(self) -> str:
        return 'V&A: David Bowie'

    def get_auctions(self) -> List[Auction]:
        url = f'https://www.vam.ac.uk/shop/david-bowie/true?cgid=david-bowie&prefn1=vamSearchable&prefv1=true&srule=Recently%20added&start=0&sz=23' # noqa

        auctions = []

        r = httpx.get(url=url)
        soup = BeautifulSoup(r.text, 'html.parser')

        items = soup.select('div.b-product')
        for item in items:
            title = item.select_one('p.u-product-tile-name').text.strip()
            link = 'https://www.vam.ac.uk' + item.select_one('a')['href']
            image_link = item.select_one('source')['data-srcset'].replace('sw=244&sh=244&sm=fit', 'sw=520&sh=520')
            _flash = item.select_one('span.u-priceinfo').text.strip()
            _price = item.select_one('span.u-value').text.strip()
            description = f'{_flash}\n{_price}'
            auction_id = f'{_flash}_{title}'.replace(' ', '_').lower()

            auctions.append(
                Auction(auction_id=auction_id,
                        description=description,
                        image_link=image_link,
                        link=link,
                        title=title
                        )
            )

        return auctions
