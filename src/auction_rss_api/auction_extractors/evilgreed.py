from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class EvilGreed(ShopifyExtractor):
    collection: str | None = None

    @property
    def domain(self) -> str:
        return f"evilgreed.com"

    @property
    def site_desc(self) -> str:
        return f"EvilGreed ({self.collection})"
