import itertools
from pprint import pprint
from typing import List, Dict, Any

import httpx
import asyncio
# import requests
import xmltodict
from bs4 import BeautifulSoup

from auction_extractors.base import AuctionExtractorAsync
from models import AuctionSearchResponse, Auction


# TODO scrape HTML marketplace page instead of using the xml version - get item image, shipping costs a.o.


class DiscogsWantlistAsync(AuctionExtractorAsync):
    search_term: str
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:111.0) Gecko/20100101 Firefox/111.0'
    }
    discogs_logo = 'https://st.discogs.com/0a84c7967109f1985415586f903c0f9e93e01e60/images/discogs-logo.svg'

    async def _get_offer_page(self, item_id: int) -> str:
        url = f"https://www.discogs.com/sell/release/{item_id}"
        params = {
            'ev': 'rb',
            'output': 'rss'}

        response = httpx.get(url=url, params=params, headers=self.headers, follow_redirects=True)
        return response.text

    async def _get_offers(self, offer_page) -> List[Dict[str, Any]]:
        """From an offer page in rss format, get the listed offers"""
        result = xmltodict.parse(offer_page)
        entries = result['feed'].get('entry')
        if isinstance(entries, list):
            return [{
                'updated': item['updated'],
                'link': item['link']['@href'],
                'title': item['title'],
                'text': item['summary']['#text']
            } for item in result['feed']['entry']]
        elif isinstance(entries, dict):
            item = entries
            return [{
                'updated': item['updated'],
                'link': item['link']['@href'],
                'title': item['title'],
                'text': item['summary']['#text']
            }]

    async def _get_wantlist(self) -> List[int]:
        """Get a users wantlist in the form of a list of item id's."""
        url = f'https://www.discogs.com/wantlist'
        params = {
            'page': 1,
            'limit': 250,
            'user': self.search_term
        }
        r = httpx.get(url=url, params=params, follow_redirects=True)
        soup = BeautifulSoup(r.content, 'html.parser')
        links = soup.findAll('span', {'class': 'marketplace_for_sale_count'})
        result = []
        for link in links:
            link = link.find('a')['href']
            item_id = link.split('?')[0].split('/')[-1]
            result.append(item_id)

        return result

    async def search(self) -> AuctionSearchResponse:
        wantlist = await self._get_wantlist()
        offer_pages = await asyncio.gather(*[self._get_offer_page(item) for item in wantlist])
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

        return AuctionSearchResponse(
            search_link=f'https://www.discogs.com/wantlist?page=1&limit=250&user={self.search_term}',
            search_term=self.search_term,
            site_desc='Discogs wantlist',
            auctions=rss_items
        )


# async def main():
#     d = DiscogsWantlist(search_term='maartenkwant')
#     result = await d.search()
#     print(result)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
