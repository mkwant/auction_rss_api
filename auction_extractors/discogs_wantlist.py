import asyncio
import itertools
from typing import List, Dict, Any

import httpx
import xmltodict
from bs4 import BeautifulSoup

from auction_extractors.base import AuctionExtractorAsync
from app.models import Auction


# TODO Use cloudscraper to bypass Cloudflare challenge

class DiscogsWantlist(AuctionExtractorAsync):
    search_term: str
    headers: dict = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:111.0) Gecko/20100101 Firefox/111.0'
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
        params = {
            'ev': 'rb',
            'output': 'rss'}

        response = await client.get(url=url, params=params)
        return response.text

    @staticmethod
    async def _get_offers(offer_page) -> List[Dict[str, Any]]:
        """From an offer page in rss format, get the listed offers"""
        result = xmltodict.parse(offer_page)
        entries = result['feed'].get('entry')
        if isinstance(entries, list):
            return [
                {
                    'updated': item['updated'],
                    'link': item['link']['@href'],
                    'title': item['title'],
                    'text': item['summary']['#text']
                } for item in result['feed']['entry']
            ]
        elif isinstance(entries, dict):
            item = entries
            return [
                {
                    'updated': item['updated'],
                    'link': item['link']['@href'],
                    'title': item['title'],
                    'text': item['summary']['#text']
                }
            ]

    async def _get_wantlist(self, client: httpx.AsyncClient) -> List[int]:
        """Get a users wantlist in the form of a list of item id's."""
        url = f'https://www.discogs.com/wantlist'
        params = {
            'page': 1,
            'limit': 250,
            'user': self.search_term
        }
        r = await client.get(url=url, params=params)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features='html.parser')
        links = soup.select('span.marketplace_for_sale_count')
        print(soup.prettify())
        result = []
        for link in links:
            link = link.find('a')['href']
            item_id = link.split('?')[0].split('/')[-1]
            result.append(int(item_id))

        return result

    async def get_auctions(self) -> List[Auction]:

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
        for offer in sorted(offers, key=lambda x: x['updated'], reverse=True):
            offer_dict = {
                'title': offer['title'],
                'auction_id': offer['link'].split('/')[-1],
                'description': offer['text'],
                'image_link': self.discogs_logo,
                'link': offer['link'],
                'seller': offer['text'].split(' - ')[1],
                'start_date': offer['updated']
            }
            rss_items.append(
                Auction(**offer_dict)
            )

        return rss_items
