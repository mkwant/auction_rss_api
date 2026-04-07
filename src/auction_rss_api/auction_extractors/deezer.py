from typing import List

import dateparser
import requests

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


class Deezer(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://www.deezer.com/search/{self.search_term}'

    @property
    def site_desc(self) -> str:
        return 'Deezer'

    def get_auctions(self) -> List[Auction]:
        auctions = []

        artist_url = f'https://api.deezer.com/search/artist/?q={self.search_term}&index=0&&output=json'
        r = requests.get(artist_url)
        artist = r.json()['data'][0]
        artist_name = artist['name']
        url = f'https://api.deezer.com/artist/{artist['id']}/albums'

        album_list = []

        while True:
            r = requests.get(url=url).json()
            album_list += r['data']
            if r.get('next'):
                url = r['next']
            else:
                break

        for album in album_list:
            item_id = str(album['id'])
            title = f"{artist_name} - {album['title']}"
            link = album['link']
            image_link = album['cover_xl']
            start_date = dateparser.parse(album['release_date'])
            description = album['record_type']

            auction = {
                'auction_id': item_id,
                'description': description,
                'link': link,
                'image_link': image_link,
                'title': title,
                'start_date': start_date
            }

            auctions.append(
                Auction(**auction)
            )

            auctions = sorted(auctions, key=lambda x: x.start_date, reverse=True)

        return auctions
