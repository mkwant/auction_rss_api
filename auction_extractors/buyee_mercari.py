import asyncio
from datetime import datetime
from typing import List

import httpx
import translators
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError

from auction_extractors.base import AuctionExtractorAsync
from models import AuctionSearchResponse, Auction


class BuyeeMercari(AuctionExtractorAsync):
    search_term: str
    translate_titles = True

    async def _get_page(self, client: httpx.AsyncClient) -> httpx.Response:
        """Retrieve search page."""
        url = 'https://buyee.jp/mercari/search'
        params = {'keyword': self.search_term, 'status': 'all'}
        r = await client.get(url=url, params=params)
        return r

    @staticmethod
    async def _parse_page(page: str) -> List[Auction]:
        """Parse search page."""
        soup = BeautifulSoup(page, 'html.parser')

        auction_list = soup.find('ul', {'class': 'item-lists'})
        auctions_source = auction_list.findAll('li', {'class': 'list'})
        auctions = []

        for auction in auctions_source:
            title = auction.find('h2', {'class': 'name'}).text
            link = f"https://buyee.jp{auction.find('a')['href'].split('?')[0]}"
            auction_id = link.split('/')[-1]
            image_link = f"https://static.mercdn.net/item/detail/orig/photos/{auction_id}_1.jpg"
            _price_yen = auction.find('p', {'class': 'price'}).text
            _price_eur = auction.find('p', {'class': 'price-fx'}).text
            _sold_out = auction.find('div', {'class': 'soldOut__text'})
            if _sold_out:
                description = f'{_sold_out.text} - {_price_yen} {_price_eur}'
            else:
                description = f'{_price_yen} {_price_eur}'

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

    @staticmethod
    async def _translate_auction(auction: Auction,
                                 from_lang: str,
                                 to_lang: str = 'en',
                                 translator: str = 'bing') -> Auction:
        """Translate the auction title. Append the original title to the description."""
        original_title = auction.title
        try:
            translated_title = translators.translate_text(query_text=auction.title,
                                                          from_language=from_lang,
                                                          to_language=to_lang,
                                                          translator=translator)
        except HTTPError:
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
                *[self._translate_auction(auction, from_lang='ja') for auction in auction_list])

        return AuctionSearchResponse(search_link=str(page.url),
                                     search_term=self.search_term,
                                     site_desc='Buyee (Mercari)',
                                     auctions=auction_list)
