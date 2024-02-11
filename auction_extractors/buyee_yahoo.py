import asyncio
from datetime import datetime
from typing import List

import httpx
from bs4 import BeautifulSoup
from httpx import HTTPError

from auction_extractors.base import AuctionExtractorAsync
from dependencies.translate import translate_text
from models import AuctionSearchResponse, Auction


# TODO Translate
# TODO Multiple pages? / keep in db?


class BuyeeYahoo(AuctionExtractorAsync):
    search_term: str
    translate_titles = True
    ms_translate_api_key: str
    ms_translate_api_location: str

    async def _get_page(self, client: httpx.AsyncClient) -> httpx.Response:
        """Retrieve search page."""
        url = f'https://buyee.jp/item/search/query/{self.search_term}'
        params = {'sort': 'end',
                  'order': 'd',
                  'conversionType': 'top_page_search',
                  'new': 1,
                  'translationType': 1}

        r = await client.get(url=url, params=params)
        return r

    @staticmethod
    async def _parse_page(page: str) -> List[Auction]:
        soup = BeautifulSoup(page, 'html.parser')

        auctions = []

        for auction in soup.findAll("div", {"class": "itemCard__item"}):
            title = auction.find("div", {"class": "itemCard__itemName"}).text.strip()
            _url_ext = auction.find("div", {"class": "itemCard__itemName"}).find("a")["href"].split('?')[0]
            link = f"https://buyee.jp{_url_ext}"
            auction_id = _url_ext.split('/')[-1]
            _image_thumb = auction.select_one('img.g-thumbnail__image')["data-src"]
            image_link = _image_thumb.replace('wing-auctions.c.yimg.jp/sim?furl=', '').split('&')[0]
            _auction_price = auction.find_all("div", {"class": "g-priceDetails"})[0].get_text(separator=' ', strip=True)
            _auction_days_left = auction.find("li", {"class": "itemCard__infoItem"}).find("span", {
                "class": "g-text g-text--attention"}).text
            description = f'<b>{_auction_price}<br><b>Time left:</b> {_auction_days_left}<br>'

            auctions.append(Auction(title=title,
                                    auction_id=auction_id,
                                    description=description,
                                    link=link,
                                    image_link=image_link,
                                    start_date=datetime.now()))

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
                                              from_lang='ja') for auction in auction_list])

        return AuctionSearchResponse(search_link=str(page.url),
                                     search_term=self.search_term,
                                     site_desc='Buyee (Yahoo)',
                                     auctions=auction_list)
