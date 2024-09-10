import urllib.parse
from datetime import datetime
from typing import List

import cloudscraper as cloudscraper
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from models.auctionextractor import AuctionExtractor
from models.auction import Auction


class Delcampe(AuctionExtractor):
    search_term: str
    URL: str = 'https://www.delcampe.net/en_GB/collectables/search'

    @property
    def site_desc(self) -> str:
        return 'Delcampe'

    @property
    def search_link(self) -> str:
        return f'https://www.delcampe.net/en_GB/collectables/search?term={self.search_term}'

    def _get_auctions(self) -> ResultSet:
        params = {'term': self.search_term}

        # Setting cookies to make the seller name and rating appear in the results
        cookies = {
            'delcampe_cookie_visitor':
                urllib.parse.quote(
                    'a:4:{s:31:"marketplace.search.default.size";s:2:"60";s:31:"marketplace.search.default.view";s:7:'
                    '"gallery";s:45:"marketplace.search.item_card.item_card_option";a:1:{s:7:"options";a:9:{s:14:'
                    '"remaining_time";b:0;s:11:"seller_name";b:1;s:8:"end_date";b:0;s:19:"seller_account_type";b:0'
                    ';s:10:"categories";b:0;s:7:"country";b:0;s:7:"payment";b:0;s:6:"seller";b:1;s:15:"spoken_language"'
                    ';b:0;}}s:41:"marketplace.search.default.advancedSearch";a:36:{s:4:"term";s:5:"bowie";s:10:'
                    '"categories";N;s:14:"excluded_terms";N;s:7:"country";N;s:11:"search_mode";s:3:"all";s:29:'
                    '"is_searchable_in_translations";N;s:29:"is_searchable_in_descriptions";N;s:10:"seller_ids";N;s:10:'
                    '"show_types";a:4:{i:0;s:11:"fixed_price";i:1;s:15:"bids_with_offer";i:2;s:18:"bids_without_offer";'
                    'i:3;s:14:"auction_houses";}s:9:"show_type";s:3:"all";s:5:"order";s:19:"sale_start_datetime";s:21:'
                    '"view_filters_reminder";b:1;s:4:"view";s:7:"gallery";s:12:"display_only";N;s:15:"display_ongoing";'
                    's:7:"ongoing";s:13:"display_state";s:7:"ongoing";s:18:"duration_selection";s:3:"all";s:12:'
                    '"started_days";N;s:13:"started_hours";N;s:11:"ended_hours";N;s:15:"payment_methods";a:2:'
                    '{i:0;s:6:"paypal";i:1;s:12:"delcampe_pay";}s:22:"payment_method_choices";a:2:{i:0;s:6:"paypal";'
                    'i:1;s:12:"delcampe_pay";}s:19:"seller_localisation";N;s:27:"seller_localisation_country";s:0:"";s:'
                    '29:"seller_localisation_continent";s:0:"";s:26:"seller_localisation_choice";s:5:"world";s:13:'
                    '"discard_users";a:0:{}s:9:"min_price";N;s:9:"max_price";N;s:19:"min_price_converted";N;s:19:'
                    '"max_price_converted";N;s:8:"currency";s:3:"all";s:25:"exclude_empty_description";b:0;s:4:"slug";'
                    'N;s:23:"is_auction_house_seller";b:0;s:15:"hasFreeDelivery";b:0;}}'
                )
        }

        scraper = cloudscraper.create_scraper()

        r = scraper.get(self.URL, params=params, cookies=cookies)
        soup = BeautifulSoup(r.content, features='html.parser')
        site_auctions = soup.select('div.item-bloc')
        return site_auctions

    def get_auctions(self) -> List[Auction]:
        auctions = []

        for auction in self._get_auctions():
            image_link = auction.select_one('a.img-view')['href']
            auction_id = auction.select_one('a.img-view')['data-item-id']
            link = f"https://www.delcampe.net{auction.select_one('a.item-link')['href']}"
            title = auction.select_one('h2.item-title').text
            _price = auction.select_one('strong.item-price').text
            _item_type = auction.select_one('div.selling-type')['title']
            desc = f'{_item_type} | {_price}'

            _seller_name = auction.select_one('div.option-content>a').text
            try:
                _seller_percentage = auction.select_one('span.percentage').text
            except AttributeError:
                _seller_percentage = '?%'

            try:
                _seller_number = auction.select_one('span.number').text.replace('(', '').replace(')', '')
            except AttributeError:
                _seller_number = '?x'

            seller = f"{_seller_name} ({_seller_percentage} / {_seller_number})"

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=desc,
                    image_link=image_link,
                    link=link,
                    title=title,
                    seller=seller
                )
            )

        return auctions
