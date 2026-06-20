from datetime import datetime
from typing import List

import httpx

from auction_rss_api.models.auction import Auction
from auction_rss_api.models.auctionextractor import AuctionExtractor


class VinylAlert(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return "https://www.vinylalert.com/releases/new"

    @property
    def site_desc(self) -> str:
        return "VinylAlert"

    def get_auctions(self) -> List[Auction]:
        r = httpx.get(url='https://vrh708nzb0.execute-api.eu-central-1.amazonaws.com/dev/releases/public')
        r.raise_for_status()
        releases = r.json()

        auctions = []
        for release in releases:
            if self.search_term is not None and self.search_term.lower() not in release['artist'].lower():
                continue

            unique_id = release['releaseId']

            if release['shipsFrom'] is None or release['shipsFrom'] == []:
                title = f"[{release['source']}] {release['artist']} - {release['title']}"
            else:
                ships_from = ', '.join(release['shipsFrom'])
                title = f"[{release['source']} ({ships_from})] {release['artist']} - {release['title']}"

            link = release['purchaseUrl']
            image_link = release.get('imageUrl')
            published = datetime.fromtimestamp(release['discoveredTimestamp'])

            auctions.append(
                Auction(
                    auction_id=unique_id,
                    title=title,
                    link=link,
                    image_link=image_link,
                    start_date=published,
                    description='',
                )
            )

        return auctions
