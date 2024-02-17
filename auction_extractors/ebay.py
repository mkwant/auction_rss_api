import base64
from datetime import datetime
from enum import Enum

import httpx
import pytz

from auction_extractors.base import AuctionExtractor
from models import Auction, AuctionSearchResponse


# TODO fix search_link.
# TODO Use https://github.com/matecsaj/ebay_rest/blob/main/src/ebay_rest/references/marketplace_id_values.json ?

class Ebay(AuctionExtractor):
    """A wrapper class around the Ebay api."""
    app_id: str
    app_secret: str
    ru_name: str
    site_id: str
    search_term: str

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

    def search(self) -> AuctionSearchResponse:
        auctions = []
        country = self.site_id.split('-')[1]

        params = {
            'q': self.search_term,
            'sort': 'newlyListed',
            'limit': 200,
            'filter': f'buyingOptions:{{FIXED_PRICE|AUCTION|BEST_OFFER}},itemLocationCountry:{country}'
        }

        headers = {
            'Authorization': f'Bearer {self.token}',
            'X-EBAY-C-MARKETPLACE-ID': self.site_id
        }
        endpoint = 'https://api.ebay.com/buy/browse/v1/item_summary/search'

        r = httpx.get(url=endpoint, headers=headers, params=params)

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

        return AuctionSearchResponse(
            search_link='ebay.com',
            search_term=self.search_term,
            site_desc=f'Ebay: {self.site_id}',
            auctions=auctions
        )


class SiteId(Enum):
    """The Ebay site id you want to use to search."""
    EBAY_AT = 'EBAY-AT'
    EBAY_AU = 'EBAY-AU'
    EBAY_CH = 'EBAY-CH'
    EBAY_DE = 'EBAY-DE'
    EBAY_ENCA = 'EBAY-ENCA'
    EBAY_ES = 'EBAY-ES'
    EBAY_FR = 'EBAY-FR'
    EBAY_FRBE = 'EBAY-FRBE'
    EBAY_FRCA = 'EBAY-FRCA'
    EBAY_GB = 'EBAY-GB'
    EBAY_HK = 'EBAY-HK'
    EBAY_IE = 'EBAY-IE'
    EBAY_IN = 'EBAY-IN'
    EBAY_IT = 'EBAY-IT'
    EBAY_MOTOR = 'EBAY-MOTOR'
    EBAY_MY = 'EBAY-MY'
    EBAY_NL = 'EBAY-NL'
    EBAY_NLBE = 'EBAY-NLBE'
    EBAY_PH = 'EBAY-PH'
    EBAY_PL = 'EBAY-PL'
    EBAY_SG = 'EBAY-SG'
    EBAY_US = 'EBAY-US'
