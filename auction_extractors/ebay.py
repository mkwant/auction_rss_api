import base64
from datetime import datetime
from enum import Enum
from typing import List

import httpx
import pytz

from auction_extractors.base import AuctionExtractor
from models import Auction


class Ebay(AuctionExtractor):
    """A wrapper class around the Ebay api."""

    @property
    def site_desc(self) -> str:
        return f'Ebay: {self.site_id}'

    @property
    def search_link(self) -> str:
        return self._search_link

    @search_link.setter
    def search_link(self, value):
        self._search_link = value

    app_id: str
    app_secret: str
    ru_name: str
    site_id: str
    search_term: str
    only_locally_listed_items: bool = True

    @property
    def token(self) -> str:
        client = httpx.Client()

        oauth_creds = base64.b64encode(f'{self.app_id}:{self.app_secret}'.encode())

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {oauth_creds.decode()}'
        }
        payload = {
            'grant_type': 'client_credentials',
            'redirect_uri': self.ru_name,
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        url = 'https://api.ebay.com/identity/v1/oauth2/token'
        r = client.post(url=url, headers=headers, data=payload)
        return r.json()['access_token']

    def get_auctions(self) -> List[Auction]:
        auctions = []

        domain = site_id_meta[self.site_id]['domain']
        self.search_link = f"{domain}/sch/i.html?_from=R40&_nkw={self.search_term}&_sacat=0&_sop=10"

        # Build search filter
        search_filter = 'buyingOptions:{FIXED_PRICE|AUCTION|BEST_OFFER}'
        if self.only_locally_listed_items:
            country = site_id_meta[self.site_id]['country_code']
            search_filter += f',itemLocationCountry:{country}'
            self.search_link += '&LH_PrefLoc=1'
        else:
            search_filter += f',itemLocationRegion:WORLDWIDE'
            self.search_link += '&LH_PrefLoc=98'

        params = {
            'q': self.search_term,
            'sort': 'newlyListed',
            'limit': 200,
            'filter': search_filter
        }

        headers = {
            'Authorization': f'Bearer {self.token}',
            'X-EBAY-C-MARKETPLACE-ID': self.site_id
        }
        api_endpoint = 'https://api.ebay.com/buy/browse/v1/item_summary/search'

        r = httpx.get(url=api_endpoint, headers=headers, params=params)

        for item in r.json()['itemSummaries']:
            auction_id = item['itemId'].split('|')[1]
            title = item['title']
            link = item['itemWebUrl'].split('?')[0]
            try:
                image_link = item['thumbnailImages'][0]['imageUrl']
            except KeyError:
                image_link = ''
            start_date = datetime.fromisoformat(item['itemCreationDate'][:-1]).replace(
                tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone('Europe/Amsterdam'))
            seller = f"{item['seller']['username']} ({item['seller']['feedbackScore']} / " \
                     f"{item['seller']['feedbackPercentage']}%)"

            description = ''
            if 'AUCTION' in item['buyingOptions']:
                auction_price = f"{item['currentBidPrice']['currency']} {item['currentBidPrice']['value']} " \
                                f"({item['bidCount']} bids)"
                item_end_date = datetime.fromisoformat(item['itemEndDate'][:-1]).replace(
                    tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone('Europe/Amsterdam'))
                description += f"{auction_price}\nEnd Date: {item_end_date:%Y-%m-%d %H:%M:%S}\n"
            if 'FIXED_PRICE' in item['buyingOptions']:
                bin_price = f"{item['price']['currency']} {item['price']['value']}"
                description += f'Buy It Now for: {bin_price}\n'
            description = description.strip()

            auctions.append(
                Auction(
                    auction_id=auction_id,
                    description=description,
                    image_link=image_link,
                    link=link,
                    title=title,
                    seller=seller,
                    start_date=start_date
                )
            )

        return auctions


class SiteId(Enum):
    """The Ebay site id you want to use to search."""
    EBAY_AT = 'EBAY-AT'
    EBAY_AU = 'EBAY-AU'
    EBAY_BEFR = 'EBAY-BEFR'
    EBAY_BENL = 'EBAY-BENL'
    EBAY_CAEN = 'EBAY-CAEN'
    EBAY_CAFR = 'EBAY-CAFR'
    EBAY_CH = 'EBAY-CH'
    EBAY_DE = 'EBAY-DE'
    EBAY_ES = 'EBAY-ES'
    EBAY_FR = 'EBAY-FR'
    EBAY_GB = 'EBAY-GB'
    EBAY_HK = 'EBAY-HK'
    EBAY_IE = 'EBAY-IE'
    EBAY_IT = 'EBAY-IT'
    EBAY_MOTOR = 'EBAY-MOTOR'
    EBAY_MY = 'EBAY-MY'
    EBAY_NL = 'EBAY-NL'
    EBAY_PH = 'EBAY-PH'
    EBAY_PL = 'EBAY-PL'
    EBAY_SG = 'EBAY-SG'
    EBAY_US = 'EBAY-US'


site_id_meta = {
    'EBAY-AT': {'country_code': 'AT', 'domain': 'https://www.ebay.at'},
    'EBAY-AU': {'country_code': 'AU', 'domain': 'https://www.ebay.com.au'},
    'EBAY-BEFR': {'country_code': 'BE', 'domain': 'https://www.befr.ebay.be'},
    'EBAY-BENL': {'country_code': 'BE', 'domain': 'https://www.benl.ebay.be'},
    'EBAY-CAEN': {'country_code': 'CA', 'domain': 'https://www.ebay.ca'},
    'EBAY-CAFR': {'country_code': 'CA', 'domain': 'https://www.cafr.ebay.ca'},
    'EBAY-CH': {'country_code': 'CH', 'domain': 'https://www.ebay.ch'},
    'EBAY-DE': {'country_code': 'DE', 'domain': 'https://www.ebay.de'},
    'EBAY-ES': {'country_code': 'ES', 'domain': 'https://www.ebay.es'},
    'EBAY-FR': {'country_code': 'FR', 'domain': 'https://www.ebay.fr'},
    'EBAY-GB': {'country_code': 'GB', 'domain': 'https://www.ebay.co.uk'},
    'EBAY-HK': {'country_code': 'HK', 'domain': 'https://www.ebay.com.hk'},
    'EBAY-IE': {'country_code': 'IE', 'domain': 'https://www.ebay.ie'},
    'EBAY-IT': {'country_code': 'IT', 'domain': 'https://www.ebay.it'},
    'EBAY-MOTOR': {'country_code': 'US', 'domain': 'https://www.ebay.com/motors'},
    'EBAY-MY': {'country_code': 'MY', 'domain': 'https://www.ebay.com.my'},
    'EBAY-NL': {'country_code': 'NL', 'domain': 'https://www.ebay.nl'},
    'EBAY-PH': {'country_code': 'PH', 'domain': 'https://www.ebay.ph'},
    'EBAY-PL': {'country_code': 'PL', 'domain': 'https://www.ebay.pl'},
    'EBAY-SG': {'country_code': 'SG', 'domain': 'https://www.ebay.com.sg'},
    'EBAY-US': {'country_code': 'US', 'domain': 'https://www.ebay.com'},
}
