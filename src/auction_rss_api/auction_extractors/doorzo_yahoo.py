from typing import List

import httpx

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class DoorzoYahoo(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.doorzo.com/en/mall/yahoo/search?cat=&name=&fid=all&sid=&keywords={self.search_term}&sort=[%22new%22]&pType=[%22currentprice%22]&seller=[%22%22]&condition=[%220%22]"

    @property
    def site_desc(self) -> str:
        return "Doorzo (Yahoo)"

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
            image_link = item['ImageUrl'].split('?')[0]
            title = item['Name']
            seller = item['SellerName']
            description = f"Remaining Time: {item['RemainingTime']}\nBid Price: {item['BidJPYPriceStr']} YEN"

            if item['BuyNowPriceStr'] != '0':
                description += f"\nBuy Now: {item['BuyNowPriceStr']} YEN"

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
