from functools import cached_property
from typing import List

import httpx

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor, logger


class DoorzoYahoo(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.doorzo.com/en/mall/yahoo/search?cat=&name=&fid=all&sid=&keywords={self.search_term}&sort=[%22new%22]&pType=[%22currentprice%22]&seller=[%22%22]&condition=[%220%22]"

    @property
    def site_desc(self) -> str:
        return "Doorzo (Yahoo)"

    @cached_property
    def exchange_rate(self) -> float | int:
        params = {
            'n': 'Sig.Front.Front.GetCurrencyExchangeRate',
            'from': 'INTERNATIONAL',
            'isNew': '15',
            'language': 'en',
            'currency': 'EUR',
        }

        r = httpx.get(url='https://sig.doorzo.com/', params=params)
        r.raise_for_status()
        try:
            rate = r.json()['data']['exchange']
        except Exception as e:
            logger.warn(f"Error getting exchange rate: {e}")
            rate = 0

        return rate

    def get_buyee_link(self, doorzo_link: str) -> str:
        hex_url = doorzo_link.split('/')[-1]
        original_url = bytes.fromhex(hex_url).decode('utf-8')
        buyee_id = original_url.split('/')[-1]
        return f'https://buyee.jp/item/jdirectitems/auction/{buyee_id}'

    def get_auctions(self) -> List[Auction]:
        params = {
            'n': 'Sig.Front.SubSite.AppYahoo.Search',
            'from': 'INTERNATIONAL',
            'isNew': '15',
            'language': 'en',
        }

        payload = {
            'keyword': self.search_term,
            'keywords': self.search_term,
            'page': 1,
            'fixed': '1',
            'cat': '',
            'goodsStatus': '',
            'sellerType': '',
            'pType': 'currentprice',
            'shipmentType': '',
            'is_appraisal': '',
            'sort': 'new',
        }

        r = httpx.post(url='https://sig.doorzo.com/', params=params, json=payload)
        r.raise_for_status()

        auctions = []

        for item in r.json()['data']['list']:
            auction_id = item['Asin']
            link = f'https://www.doorzo.com/en/mall/yahoo/detail/{item['Url']}'
            buyee_link = self.get_buyee_link(doorzo_link=link)
            image_link = item['ImageUrl'].split('?')[0]
            title = item['Name']
            seller = item['SellerName']
            description = f"Bid Price: JPY {item['BidJPYPrice']:,} (Eur {self.exchange_rate * item['BidJPYPrice']:.2f})"

            if item['BuyNowPriceStr'] != '0':
                description += f"\nBuy Now: JPY {item['BuyNowPrice']:,} (Eur {self.exchange_rate * item['BuyNowPrice']:.2f})"

            description += f"\n\n<a href='{buyee_link}'>Buyee</a>"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    link=link,
                    image_link=image_link,
                    title=title,
                    description=description,
                    seller=seller,
                )
            )

        return auctions
