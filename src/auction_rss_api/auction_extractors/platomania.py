import json
from typing import List
from urllib.parse import urljoin

import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor

BASE_URL = "https://www.platomania.nl"


class PlatoMania(AuctionExtractor):
    search_term: str

    @property
    def search_link(self) -> str:
        return f"{BASE_URL}/search/results/?q={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "Platomania"

    def get_auctions(self) -> List[Auction]:
        r = httpx2.get(url=self.search_link)
        r.raise_for_status()

        soup = BeautifulSoup(r.content, features='html.parser')
        # The page renders every result twice (mobile list + desktop grid); use the grid only
        cards = soup.select('[data-testid="search-results-grid"] div.product-card')

        items = []

        for card in cards:
            link_el = card.select_one('a[data-select-item]')
            data = json.loads(link_el['data-select-item'])

            href = str(link_el['href'])
            item_id = href.split('/')[2]
            link = urljoin(base=BASE_URL, url=href)

            artist = data.get('artist', '')
            title = f"{artist} - {data['title']}" if artist else data['title']

            img = card.select_one('img')
            image_link = urljoin(base=BASE_URL, url=img['src']) if img and img.get('src') else ''

            price = card.select_one('[data-testid="article-price"]').text.strip()
            stock_el = card.select_one('[data-testid="card-stock"]')
            stock = stock_el.text.strip() if stock_el else ''
            details = ' | '.join(x for x in (data.get('format'), data.get('label')) if x)

            description = f"{price} - {details}\n\n{stock}".strip()

            items.append(
                Auction(
                    auction_id=item_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return items
