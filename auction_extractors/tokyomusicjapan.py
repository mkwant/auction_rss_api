from datetime import datetime

import requests

from auction_extractors.base import AuctionExtractor
from models import AuctionSearchResponse, Auction


class TokyoMusicJapan(AuctionExtractor):
    search_term: str

    def _get_auctions(self) -> list:
        url = 'https://www.tokyomusicjapan.com/service/api/ArtistSearch?artist=new&currency=USD&isGeneral=true'
        r = requests.get(url=url)
        items = [x for x in r.json() if self.search_term.lower() in x['Artist'].lower()]
        return items

    def search(self) -> AuctionSearchResponse:
        auctions = []

        for item in self._get_auctions():
            auction_id = item['Id']
            title = f"{item['Title']} ({item['Notes']})"
            link = 'http://tokyomusicjapan.com/new.html'
            image_link = item['Url']
            description = '\n'.join([
                f"Format: {item['Format']}",
                f"Cat no: {item['CatNb']}",
                f"Disc: {item['Dsk']}",
                f"Sleeve: {item['Slv']}",
                f"Price: ${item['Price']:.2f}"
            ])

            auctions.append(Auction(auction_id=auction_id,
                                    description=description,
                                    image_link=image_link,
                                    link=link,
                                    title=title,
                                    start_date=datetime.now()
                                    ))

        return AuctionSearchResponse(
            search_link=f'http://tokyomusicjapan.com/new.html',
            search_term=self.search_term,
            site_desc=f'TokyoMusicJapan',
            auctions=auctions
        )
