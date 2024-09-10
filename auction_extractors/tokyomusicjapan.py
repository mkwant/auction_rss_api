from datetime import datetime
from typing import List

import requests

from models.auctionextractor import AuctionExtractor
from models.auction import Auction


class TokyoMusicJapan(AuctionExtractor):
    search_term: str

    @property
    def site_desc(self) -> str:
        return 'TokyoMusicJapan'

    @property
    def search_link(self) -> str:
        return 'http://tokyomusicjapan.com/new.html'  # noqa

    def _get_auctions(self) -> list:
        url = 'https://www.tokyomusicjapan.com/service/api/ArtistSearch?artist=new&currency=USD&isGeneral=true'
        r = requests.get(url=url)
        items = [x for x in r.json() if self.search_term.lower() in x['Artist'].lower()]
        return items

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for item in self._get_auctions():
            auction_id = item['Id']
            title = f"{item['Title']} ({item['Notes']})"
            link = 'http://tokyomusicjapan.com/new.html'  # noqa
            image_link = item['Url']
            description = '\n'.join(
                [
                    f"Format: {item['Format']}",
                    f"Cat no: {item['CatNb']}",
                    f"Disc: {item['Dsk']}",
                    f"Sleeve: {item['Slv']}",
                    f"Price: ${int(item['Price']):.2f}"
                ]
            )

            auctions.append(
                Auction(auction_id=auction_id,
                        description=description,
                        image_link=image_link,
                        link=link,
                        title=title
                        )
            )

        return auctions
