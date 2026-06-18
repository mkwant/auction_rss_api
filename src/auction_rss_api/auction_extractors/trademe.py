import json
from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class TradeMe(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.trademe.co.nz/a/search?search_string={self.search_term}&sort_order=expirydesc&condition=used"

    @property
    def site_desc(self) -> str:
        return "TradeMe"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        cookies = {'trademeclientid': '1c161f2a-eb21-472f-9004-8f5e90252a5b'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0'}
        params = {
            'search_string': self.search_term,
            'sort_order': 'expirydesc',
            'condition': 'used',
        }
        r = httpx.get(
            url='https://www.trademe.co.nz/a/search',
            params=params,
            cookies=cookies,
            headers=headers,
        )
        r.raise_for_status()

        soup = BeautifulSoup(markup=r.text, features='html.parser')
        json_str = soup.select_one('script#frend-state').text
        json_parsed = json.loads(json_str)

        items = json_parsed['NGRX_STATE']['listing']['cachedSearchResults']['entities']
        items = [items[item]['item'] for item in items]
        for item in items:
            item_id = str(item['listingId'])
            title = item['title']
            link = 'https://www.trademe.co.nz/a' + item['canonicalPath']
            try:
                image_link = item['pictureHref'].replace('thumb', 'plus')
            except KeyError:
                image_link = None

            _start_price = item['startPrice']
            try:
                _is_buy_now_only = item['isBuyNowOnly']
            except KeyError:
                _is_buy_now_only = False

            try:
                _has_buy_now = item['hasBuyNow']
            except KeyError:
                _has_buy_now = False

            if _is_buy_now_only:
                description = f"Buy It Now: ${item['buyNowPrice']:.2f}"
            elif not _has_buy_now:
                description = f"Bidding from: ${_start_price:.2f}"
            else:
                description = f"Buy It Now: ${item['buyNowPrice']:.2f}\nBidding from: ${_start_price:.2f}"

            auctions.append(
                Auction(
                    auction_id=item_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
