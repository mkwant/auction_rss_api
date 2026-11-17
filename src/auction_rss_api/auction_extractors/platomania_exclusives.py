import json
from typing import List
from urllib.parse import urljoin

import httpx2
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor

BASE_URL = 'https://www.platomania.nl'


class PlatomaniaExclusives(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'{BASE_URL}/concerto-plato-exclusives?sorteer=datum-nieuw'

    @property
    def site_desc(self) -> str:
        return 'Platomania Exclusives'

    def get_auctions(self) -> List[Auction]:
        r = httpx2.get(url=self.search_link, timeout=10.0)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')

        auctions = []
        seen = set()

        # Every result links to its article via an <a data-select-item="{json}">.
        # The page may render each result twice (desktop grid + mobile list), so dedupe by id.
        for link_el in soup.select('a[data-select-item][href^="/article/"]'):
            href = link_el['href']
            item_id = href.split('/')[2]
            if item_id in seen:
                continue
            seen.add(item_id)

            item_info = json.loads(link_el['data-select-item'])

            # In the grid the image lives in the surrounding card; in the list, inside the link itself
            container = link_el.find_parent('div', class_='product-card') or link_el
            img = container.select_one('img')
            image_link = urljoin(base=BASE_URL, url=img['src']) if img and img.get('src') else ''

            artist = item_info.get('artist', '')
            title = f"{artist} - {item_info['title']}" if artist else item_info['title']
            details = '\n'.join(
                x for x in (
                    item_info.get('format'),
                    item_info.get('label'),
                    item_info.get('genre'),
                ) if x
            )
            stock_el = container.select_one('[data-testid="card-stock"], [data-testid="row-stock"]')
            stock = stock_el.get_text(' ', strip=True).lstrip('· ') if stock_el else ''
            description = f"Prijs: Eur {item_info['price']}\n{details}\n{stock}".strip()

            auctions.append(
                Auction(
                    auction_id=item_id,
                    title=title,
                    link=urljoin(base=BASE_URL, url=href),
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
