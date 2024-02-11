import asyncio
from datetime import datetime
from typing import List

import httpx
import json
from bs4 import BeautifulSoup
from httpx import HTTPError

from auction_extractors.base import AuctionExtractorAsync
from dependencies.translate import translate_text
from models import AuctionSearchResponse, Auction


class BuyeeMercari(AuctionExtractorAsync):
    search_term: str
    translate_titles = True
    ms_translate_api_key: str
    ms_translate_api_location: str

    async def _get_page(self, client: httpx.AsyncClient) -> httpx.Response:
        """Retrieve search page."""
        url = 'https://asf.myeeglobal.com/mercari'
        params = {'keyword': self.search_term,
                  'status': 'all',
                  'conversionType': 'Mercari_DirectSearch',
                  'currencyCode': 'EUR',
                  'myee': 0,
                  'languageCode': 'en',
                  'lang': 'en'}
        r = await client.get(url=url, params=params)
        return r

    @staticmethod
    async def _parse_page(page: str) -> List[Auction]:
        """Parse search page."""
        soup = BeautifulSoup(page, 'html.parser')
        json_string = soup.find('script', {'type': 'application/json'}).contents[0]
        parsed_json = json.loads(json_string)
        auction_list = parsed_json['props']['pageProps']['catalog']['entries']

        auctions = []

        for auction in auction_list:
            title = auction['names']['ja']
            auction_id = auction['item']['code']
            link = f"https://buyee.jp/mercari/item/{auction_id}"
            image_link = f"https://static.mercdn.net/item/detail/orig/photos/{auction_id}_1.jpg"
            _price_yen = f"{auction['price']['value']:,} yen"
            _price_eur = f"€{auction['localPrice']['value']:.2f}"
            if not auction['hasStock']:
                description = f'SOLD - {_price_yen} ({_price_eur})'
            else:
                description = f'{_price_yen} ({_price_eur})'

            auctions.append(
                Auction(**{
                    'title': title,
                    'auction_id': auction_id,
                    'description': description,
                    'link': link,
                    'image_link': image_link,
                    'start_date': datetime.now()
                }))
        return auctions

    async def _translate_auction(self,
                                 client: httpx.AsyncClient,
                                 auction: Auction,
                                 from_lang: str,
                                 to_lang: str = 'en') -> Auction:
        """Translate the auction title. Append the original title to the description."""
        original_title = auction.title
        try:

            translated_title = await translate_text(
                client=client,
                text=auction.title,
                from_language=from_lang,
                to_language=to_lang,
                ms_translate_api_key=self.ms_translate_api_key,
                ms_translate_api_location=self.ms_translate_api_location)
        except (HTTPError, ConnectionError) as e:
            auction.__dict__.update({'description': f"{auction.description}\n\nTranslate failed: '{e}'"})
            return auction

        auction.__dict__.update({'title': translated_title})
        auction.__dict__.update({'description': f"{auction.description}\n\nOriginal title: '{original_title}'"})
        return auction

    async def search(self) -> AuctionSearchResponse:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            page = await self._get_page(client=client)
            auction_list = await self._parse_page(page=page.text)

            if self.translate_titles:
                auction_list = await asyncio.gather(
                    *[self._translate_auction(client=client,
                                              auction=auction,
                                              from_lang='ja')
                      for auction in auction_list
                      ])

        return AuctionSearchResponse(search_link=str(page.url),
                                     search_term=self.search_term,
                                     site_desc='Buyee (Mercari)',
                                     auctions=auction_list)
