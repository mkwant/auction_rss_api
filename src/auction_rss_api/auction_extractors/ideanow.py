from auction_rss_api.models.auctionextractor_shopify import ShopifySearchBrowserExtractor


class IdeaNow(ShopifySearchBrowserExtractor):
    @property
    def domain(self) -> str:
        return "ideanow.online"

    @property
    def site_desc(self) -> str:
        return "IdeaNow"
