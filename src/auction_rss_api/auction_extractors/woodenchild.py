from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class WoodenChild(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "wooden-child.myshopify.com"

    @property
    def site_desc(self) -> str:
        return "Wooden Child"
