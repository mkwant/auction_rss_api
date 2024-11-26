import asyncio
import json
from typing import List

import httpx
from bs4 import BeautifulSoup

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class BandcampFaves(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://bandcamp.com/{self.search_term}/following/artists_and_labels'

    @property
    def site_desc(self) -> str:
        return f'Bandcamp faves'

    @staticmethod
    async def get_bandcamp_merch(subdomain: str, client: httpx.AsyncClient) -> list[Auction]:
        """Given a subdomain, scrape the merch items."""
        auctions = []

        base_url = f"https://{subdomain}.bandcamp.com"

        r = await client.get(f'{base_url}/merch')
        soup = BeautifulSoup(r.text, features='html.parser')
        item_list = soup.select_one('ol.merch-grid')

        try:
            items = item_list.select('li.merch-grid-item')
        except AttributeError:
            return auctions

        for item in items:
            auction_id = item["data-item-id"]

            _title = ' '.join(
                ' '.join([x.strip() for x in item.select_one('p.title') if isinstance(x, str)]).strip().split())
            try:
                _artist = item.select_one('p.title>span.artist-override').text
                title = f'{_artist}: {_title}'
            except AttributeError:
                title = _title

            link = base_url + item.select_one('a')['href']

            try:
                image_link = item.select_one('img')['data-original']
            except KeyError:
                image_link = item.select_one('img')['src']
            image_link = image_link.replace('_37', '_10')

            _item_type = item.select_one('div.merchtype').text.strip()
            _price = item.select_one('p.price').text.strip()
            description = f'{_item_type}\n{_price}'

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link
                }))

        return auctions

    def get_followed_subdomains(self) -> list[str]:
        """Get the subdomains of the artist the user is following."""
        r = httpx.get(self.search_link)
        soup = BeautifulSoup(r.content, features='html.parser')
        pagedata = soup.select_one('div#pagedata')['data-blob']
        json_data = json.loads(pagedata)
        following = json_data['item_cache']['following_bands']
        following_subdomains = [following[x]['url_hints']['subdomain'] for x in following]
        return following_subdomains

    async def get_faves_merch(self) -> list[Auction]:
        tasks = []
        client = httpx.AsyncClient(follow_redirects=True)

        for subdomain in self.get_followed_subdomains():
            tasks.append(asyncio.create_task(self.get_bandcamp_merch(subdomain=subdomain, client=client)))
        faves_merch = await asyncio.gather(*tasks)

        await client.aclose()

        return [items for fave in faves_merch for items in fave]

    def get_auctions(self) -> List[Auction]:
        auctions = asyncio.run(self.get_faves_merch())
        return auctions
