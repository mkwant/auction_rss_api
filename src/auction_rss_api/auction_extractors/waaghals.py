from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class Waaghals(ShopifyExtractor):
    collection: str

    @property
    def domain(self) -> str:
        return f"shop.waaghals.com"

    @property
    def site_desc(self) -> str:
        return f"Waaghals"
