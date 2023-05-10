from enum import Enum

from auction_extractors.base import AuctionExtractor
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection

from models import Auction, AuctionSearchResponse


class Ebay(AuctionExtractor):
    """A wrapper class around the Ebay api."""
    appid: str
    site_id: str
    search_term: str

    @property
    def connection(self) -> Connection:
        """Connect to the Ebay api."""
        try:
            return Connection(appid=self.appid, siteid=self.site_id, config_file=None)
        except ConnectionError as e:
            print(e)
            print(e.response.dict())

    def search(self) -> AuctionSearchResponse:
        """Search Ebay for keywords."""
        payload = {'keywords': f'{self.search_term}',
                   'sortOrder': 'StartTimeNewest',
                   'itemFilter':
                       [
                           {'name': 'HideDuplicateItems', 'value': True},
                           {'name': 'ListedIn', 'value': self.site_id}
                       ],
                   'outputSelector':
                       ['SellerInfo']
                   }
        response = self.connection.execute('findItemsAdvanced', payload)

        auctions = []

        for item in response.reply.searchResult.item:
            # noinspection PyProtectedMember
            description = f'{item.sellingStatus.currentPrice._currencyId} ' \
                          f'{float(item.sellingStatus.currentPrice.value):.2f}\nEnd Date: {item.listingInfo.endTime}'
            if item.listingInfo.buyItNowAvailable == 'true':
                # noinspection PyProtectedMember
                description += f'\nBuy It Now for: {item.listingInfo.buyItNowPrice._currencyId} ' \
                               f'{float(item.listingInfo.buyItNowPrice.value):.2f}'
            seller = f'{item.sellerInfo.sellerUserName} ' \
                     f'({item.sellerInfo.feedbackScore} / {item.sellerInfo.positiveFeedbackPercent}%)'

            if item.galleryURL:
                item.galleryURL = item.galleryURL.replace('/thumbs', '').replace('s-l140.jpg', 's-l1600.jpg')
            else:
                item.galleryURL = ''

            auctions.append(Auction(auction_id=item.itemId,
                                    description=description,
                                    image_link=item.galleryURL,
                                    link=item.viewItemURL,
                                    title=item.title,
                                    seller=seller,
                                    start_date=item.listingInfo.startTime))

        return AuctionSearchResponse(
            search_link=response.reply.itemSearchURL,
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
