from typing import List

import requests

from models.auction import Auction
from models.auctionextractor import AuctionExtractor


# THES394093

class VandaCollection(AuctionExtractor):
    @property
    def search_link(self) -> str:
        return f'https://collections.vam.ac.uk/search/?id_category={self.search_term}&page=1&page_size=100'

    @property
    def site_desc(self) -> str:
        return 'V&A Collection'

    @staticmethod
    def get_item_page(page: int) -> dict:
        url = 'https://api.vam.ac.uk/v2/objects/search'

        params = {
            'id_category': 'THES394093',
            'page_size': 100,
            'order_by': 'place',
            'order_sort': 'asc',
            'page': page
        }
        r = requests.get(url=url, params=params)
        r.raise_for_status()
        return r.json()

    def get_all_records(self) -> list[dict]:
        page = 1
        pages = 1000

        all_records = []

        while page <= pages:
            print(f'Retrieving page {page}')
            r = self.get_item_page(page=page)
            pages = r['info']['pages']
            records = r['records']
            all_records.extend(records)
            page += 1

        all_records.sort(key=lambda x: x['systemNumber'], reverse=True)
        return all_records

    def get_auctions(self) -> List[Auction]:
        auctions = []

        records = self.get_all_records()
        for record in records[:10]:
            _title = record['_primaryTitle']
            _date = record['_primaryDate']
            _object_type = record['objectType']

            try:
                _author = record['_primaryMaker']['name']
            except KeyError:
                _author = None

            if _author:
                title = f'{_title} | {_object_type} ({_author}, {_date})'
            else:
                title = f'{_title} | {_object_type} ({_date})'

            auction_id = record['systemNumber']
            link = f'https://collections.vam.ac.uk/item/{auction_id}/'
            image_link = f'https://framemark.vam.ac.uk/collections/{record['_primaryImageId']}/full/full/0/default.jpg'
            description = f"Item_id: {auction_id}"

            auctions.append(
                Auction(auction_id=auction_id,
                        description=description,
                        image_link=image_link,
                        link=link,
                        title=title
                        )
            )

        return auctions
