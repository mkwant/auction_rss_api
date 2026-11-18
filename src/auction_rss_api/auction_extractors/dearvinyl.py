from auction_rss_api.models.auctionextractor_shopify import ShopifySearchBrowserExtractor


class DearVinyl(ShopifySearchBrowserExtractor):
    @property
    def domain(self) -> str:
        return "dearvinyl.com"

    @property
    def site_desc(self) -> str:
        return "DearVinyl"
