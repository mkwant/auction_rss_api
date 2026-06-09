from typing import List

import httpx

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class DoorzoRakuma(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.doorzo.com/en/search?fid=all&sid=&keywords={self.search_term}&sort=created_desc&identity=all&seller=[%22%22]&website=[%22rakuma%22]"

    @property
    def site_desc(self) -> str:
        return f"Doorzo (Rakuma)"

    def get_auctions(self) -> List[Auction]:
        url = "https://sig.doorzo.com/"

        params = {
            'n': 'Sig.Front.SubSite.AppGlobal.MixSearch',
            'from': 'INTERNATIONAL',
            'isNew': 15,
            'language': 'en',
            'keyword': self.search_term,
            'filter': 'lashinbang',
            'website': 'rakuma',
            'onlyInStock': 1,
            'orderBy': 'created_desc',
        }

        r = httpx.get(url=url, params=params)
        r.raise_for_status()

        items = r.json()['data']['items']

        auctions = []
        for item in items:
            auction_id = str(item['Asin'])
            link = f'https://www.doorzo.com/en/mall/rakuma/detail/{item['Url']}'
            image_link = item['ImageUrl']
            title = item['Name']
            description = f"JPY {item['JPYPrice']}"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    link=link,
                    image_link=image_link,
                    title=title,
                    description=description,
                )
            )
        return auctions
