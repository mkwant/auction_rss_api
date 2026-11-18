from auction_rss_api.models.auctionextractor_shopify import ShopifySearchBrowserExtractor


class Waxer(ShopifySearchBrowserExtractor):
    @property
    def domain(self) -> str:
        return "waxer.eu"

    @property
    def site_desc(self) -> str:
        return "Waxer"
