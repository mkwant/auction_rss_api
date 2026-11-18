from auction_rss_api.models.auctionextractor_shopify import ShopifySearchBrowserExtractor


class RedEye(ShopifySearchBrowserExtractor):
    @property
    def domain(self) -> str:
        return "redeye.com.au"

    @property
    def site_desc(self) -> str:
        return "Red Eye Records"
