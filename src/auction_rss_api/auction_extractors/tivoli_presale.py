from hashlib import md5
from typing import List

import httpx
from bs4 import BeautifulSoup

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class TivoliPresale(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f"https://ticket.tivolivredenburg.nl/nl/specialoffer/{self.search_term}"

    @property
    def site_desc(self) -> str:
        return "Tivoli presale"

    def get_auctions(self) -> List[Auction]:
        auctions = []
        r = httpx.get(self.search_link)
        r.raise_for_status()
        soup = BeautifulSoup(markup=r.text, features='html.parser')
        fields = soup.select('div.special-offer-content>div')
        fields = [x.text.strip() for x in fields if x.text.strip()]
        title = ' | '.join(fields)
        auction_id = md5(title.encode('utf-8')).hexdigest()
        description = '\n'.join(fields)
        auctions.append(
            Auction(
                auction_id=auction_id,
                title=title,
                description=description,
                link=self.search_link,
            )
        )
        return auctions
