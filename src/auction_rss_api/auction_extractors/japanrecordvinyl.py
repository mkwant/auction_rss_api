from auction_rss_api.models.auctionextractor_shopify import ShopifySearchBrowserExtractor


class JapanRecordVinyl(ShopifySearchBrowserExtractor):

    @property
    def domain(self) -> str:
        return "japan-record-vinyl.com"

    @property
    def site_desc(self) -> str:
        return "Japan Record Vinyl"
