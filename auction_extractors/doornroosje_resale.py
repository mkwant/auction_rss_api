from typing import List

import dateparser
import httpx

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class DoornroosjeResale(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://resaleagenda.doornroosje.nl/edd2f25dee0d4d4594975dd8f0dc6b10"

    @property
    def site_desc(self) -> str:
        return "Doornroosje resale"

    def get_auctions(self) -> List[Auction]:
        auctions = []

        url = 'https://shopping-api.paylogic.com/channels/edd2f25dee0d4d4594975dd8f0dc6b10'

        r = httpx.get(url=url)
        r.raise_for_status()

        items = r.json()['_embedded']['shop:event']
        for item in items:
            link = item['_links']['self']['href']
            auction_id = link.split('/')[-1]
            image_link = item['image']
            _event_name = item['title']['en']
            _event_start = dateparser.parse(item['event_start'])
            _event_end = dateparser.parse(item['event_end'])
            _event_location = item['location']['name']
            title = f'{_event_start:%a %Y-%m-%d} [{_event_location}]: {_event_name}'
            description = f"{_event_start:%Y-%m-%d %H:%M} - {_event_end:%Y-%m-%d %H:%M}"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    description=description,
                )
            )

        return auctions
