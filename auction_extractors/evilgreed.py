from models.auctionextractor_shopify import ShopifyExtractor


class EvilGreed(ShopifyExtractor):
    collection: str

    @property
    def site_desc(self) -> str:
        return f"EvilGreed ({self.collection})"

    @property
    def domain(self) -> str:
        return f"evilgreed.com/collections/{self.collection.lower().replace(' ', '-')}"
