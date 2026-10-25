from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class Rockwell(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "rockwell-4147.myshopify.com"

    @property
    def site_desc(self) -> str:
        if self.collection:
            return f"Rockwell (collection: '{self.collection}')"
        return "Rockwell"
