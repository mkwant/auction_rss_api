from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class Waaghals(ShopifyExtractor):
    collection: str

    @property
    def site_desc(self) -> str:
        return f"Waaghals ({self.collection})"

    @property
    def domain(self) -> str:
        return f"shop.waaghals.com/collections/{self.collection.lower().replace(' ', '-')}"
