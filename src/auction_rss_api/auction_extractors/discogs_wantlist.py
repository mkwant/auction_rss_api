import asyncio
import itertools
from typing import Any

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractorAsync


class DiscogsWantlist(AuctionExtractorAsync):
    search_term: str
    headers: dict = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0'
    }
    discogs_logo: str = ('https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Discogs_record_icon.svg/'
                         '480px-Discogs_record_icon.svg.png')

    @property
    def site_desc(self) -> str:
        return 'Discogs wantlist'

    @property
    def search_link(self) -> str:
        return f'https://www.discogs.com/wantlist?page=1&limit=250&user={self.search_term}'

    @staticmethod
    async def _get_offer_page(client: httpx.AsyncClient, item_id: int) -> str:
        url = f"https://www.discogs.com/sell/release/{item_id}"
        params = {'sort': 'listed,desc'}
        response = await client.get(url=url, params=params)
        return response.text

    @staticmethod
    async def _get_offers(offer_page) -> list[dict[str, Any]]:
        """From an offer page, get the listed offers"""
        item_list = []
        soup = BeautifulSoup(markup=offer_page, features='html.parser')
        items = soup.select('tr.shortcut_navigable')

        for item in items:
            title = item.select_one('a.item_description_title').text.strip()
            item_link = 'https://www.discogs.com' + str(item.select_one('a.item_description_title')['href'])
            seller = item.select_one('td.seller_info a').text.strip()

            try:
                _rating = item.select_one('span.star_rating + strong').text.strip()
                seller += f" ({_rating})"
            except AttributeError:
                pass

            _price = item.select_one('span.price').text.strip()
            _shipping = ' '.join([x.strip() for x in item.select_one('span.item_shipping').text.strip().split('\n')])
            _media_condition = item.select_one('span.mplabel.condition-label-mobile + span').text.strip().split('\n')[0]
            _sleeve_condition = item.select_one('span.item_sleeve_condition').text.strip()
            _ships_from = item.select_one('li:has(span.mplabel:-soup-contains("Ships From:"))').text.strip().replace(
                'Ships From:', '')
            description = f"Price: {_price} ({_shipping})\nMedia condition: {_media_condition}\nSleeve condition: {_sleeve_condition}\nShips from: {_ships_from}"

            item_list.append({
                'link': item_link,
                'title': title,
                'text': description,
                'seller': seller,
            })
        return item_list

    async def _get_wantlist(self, client: httpx.AsyncClient) -> list[int]:
        """Get a users wantlist in the form of a list of item id's."""
        url = 'https://www.discogs.com/wantlist'
        params = {
            'page': 1,
            'limit': 250,
            'user': self.search_term
        }
        headers = {
            'Referer': f'https://www.discogs.com/user/{self.search_term}',
            'Cache-Control': 'no-cache',
        }
        r = await client.get(url=url, params=params, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features='html.parser')
        links = soup.select('span.marketplace_for_sale_count')
        result = []
        for link in links:
            link = link.find('a')['href']
            item_id = link.split('?')[0].split('/')[-1]
            result.append(int(item_id))

        return result

    async def get_auctions(self) -> list[Auction]:

        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            wantlist = await self._get_wantlist(client)
            offer_pages = await asyncio.gather(*
                                               [
                                                   self._get_offer_page(
                                                       client=client,
                                                       item_id=item_id
                                                   ) for item_id in wantlist
                                               ]
                                               )
            offers = await asyncio.gather(*[self._get_offers(offer_page) for offer_page in offer_pages])

        offers = itertools.chain(*offers)  # flatten list of lists

        rss_items = []
        for offer in offers:
            offer_dict = {
                'title': offer['title'],
                'auction_id': offer['link'].split('/')[-1],
                'description': offer['text'],
                'image_link': self.discogs_logo,
                'link': offer['link'],
                'seller': offer['seller'],
            }
            rss_items.append(
                Auction(**offer_dict)
            )

        return rss_items
