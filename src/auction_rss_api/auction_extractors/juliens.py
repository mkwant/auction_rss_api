import datetime
from typing import List, TypeVar

import httpx

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor

T = TypeVar("T")


class JuliensAuctions(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://www.juliensauctions.com/en/search?query={self.search_term}"

    @property
    def site_desc(self) -> str:
        return "Julien's Auctions"

    def _get_auction_data(self) -> list[dict]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0',
            'accept-profile': 'public',
            'apikey': 'sb_publishable_iQTmMpf0DZCzSGfPr4Eu7A_Nf80Trrk',
        }

        params = {
            "select": "id,external_id,status,origin,start_date,description,image_url,starting_bid,current_bid,sold_price,number_of_bids,lot_number,title,low_estimate,high_estimate,is_hidden,auction_campaign!inner(id,external_id,title,type,is_hidden),associate(id,name,image_url,type)",
            "fts": f"fts.{self.search_term}:*",
            "order": "start_date.desc.nullslast,lot_number.asc",
            "offset": 0,
            "limit": 100,
        }

        r = httpx.get(
            url='https://api.juliensauctions.com/rest/v1/lot_campaign_view',
            params=params,
            headers=headers,
        )

        return r.json()

    @staticmethod
    def format_currency(price_val: T) -> T | str:
        if isinstance(price_val, int):
            return f"${price_val / 100:.2f}"
        return price_val

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for auction in self._get_auction_data():
            auction_id = auction['id']
            title = auction['title']
            link = f"https://www.juliensauctions.com/en/items/{auction_id}"
            image_link = auction['image_url']
            description = f"""
        {auction['description']}

        Status:\t\t{auction['status']}
        Starting bid:\t{self.format_currency(auction['starting_bid'])}
        Current bid:\t{self.format_currency(auction['current_bid'])}
        Sold price:\t{self.format_currency(auction['sold_price'])}
        Number of bids:\t{auction['number_of_bids']}

        Low estimate:\t{self.format_currency(auction['low_estimate'])}
        High estimate:\t{self.format_currency(auction['high_estimate'])}
            """
            campaign = auction['auction_campaign']['title']
            start_date = datetime.datetime.fromisoformat(auction['start_date'])

            auctions.append(
                Auction(
                    auction_id=str(auction_id),
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title,
                    start_date=start_date,
                    seller=campaign
                )
            )
        return auctions
