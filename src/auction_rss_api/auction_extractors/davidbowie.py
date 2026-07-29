from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class DavidBowie(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "store.davidbowie.com"

    @property
    def site_desc(self) -> str:
        return "DavidBowie Official Store"
