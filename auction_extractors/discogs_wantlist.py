from typing import List, Dict

import requests
import xmltodict as xmltodict

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class DiscogsWantlist(AuctionExtractor):
    search_term: str
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:111.0) Gecko/20100101 Firefox/111.0'
    }

    def _get_item_offers(self, item_id: int) -> List[Dict]:
        url = f"https://www.discogs.com/sell/release/{item_id}"
        params = {
            'ev': 'rb',
            'output': 'rss'}

        r = requests.get(url=url, params=params, headers=self.headers)
        result = xmltodict.parse(r.text)
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

    def _get_wantlist(self) -> List[int]:

        params = {
            'page': 1,
            'per_page': 100
        }
        r = requests.get(url=f'https://api.discogs.com/users/{self.search_term}/wants',
                         headers=self.headers, params=params)
        return [item['basic_information']['id'] for item in r.json()['wants']]

    def search(self) -> AuctionSearchResponse:
        wantlist = self._get_wantlist()
        all_offers = []
        for item in wantlist:
            offers = self._get_item_offers(item)
            if not offers:
                continue
            for offer in offers:
                all_offers.append(
                    Auction(title=offer['title'],
                            auction_id=offer['link'].split('/')[-1],
                            description=offer['text'],
                            link=offer['link'],
                            seller=offer['text'].split(' - ')[1],
                            start_date=offer['updated']
                            )
                )
        all_offers = sorted(all_offers, key=lambda x: x.start_date, reverse=True)

        return AuctionSearchResponse(
            search_link=f'https://api.discogs.com/users/{self.search_term}/wants',
            search_term=self.search_term,
            site_desc='Discogs wantlist',
            auctions=all_offers
        )
