import json
from datetime import datetime
from typing import List

import httpx

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class LiveAuctioneers(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.liveauctioneers.com/search/?keyword={self.search_term}&pageSize=48&sort=-publishDate&status=online"

    @property
    def site_desc(self) -> str:
        return "LiveAuctioneers"

    def get_auctions(self) -> List[Auction]:
        parameters = {
            "page": 1,
            "pageSize": 48,
            "searchTerm": self.search_term,
            "sort": "-publishDate",
            "status": "online",
        }

        r = httpx.get(
            url="https://search-party-prod.liveauctioneers.com/search/v4/web",
            params={
                "parameters": json.dumps(parameters, separators=(",", ":")),
                "useAuctionHouseSearchFiltering": "true",
            },
            timeout=10.0,
        )
        r.raise_for_status()

        items = r.json()["payload"]["items"]

        auctions = []

        for item in items:
            auction_id = str(item["itemId"])
            link = f"https://www.liveauctioneers.com/item/{auction_id}_{item['slugWithLocation']}"
            image_link = f"https://p1.liveauctioneers.com/{item['sellerId']}/{item['catalogId']}/{auction_id}_1_x.jpg"
            start_time = datetime.fromtimestamp(item["saleStartTs"])
            description = (
                f"Start time: {start_time}\n"
                f"Estimate: {item['currency']} "
                f"{item['lowBidEstimate']}-{item['highBidEstimate']}\n"
                f"Start bid: {item['currency']} {item['startPrice']}\n\n"
                f"{item['shortDescription']}\n\n"
                f"{item['catalogTitle']}"
            )

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=item["title"],
                    seller=item["sellerName"],
                )
            )

        return sorted(
            auctions,
            key=lambda auction: auction.auction_id,
            reverse=True,
        )
