from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class Foetus(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "179ef1-12.myshopify.com"

    @property
    def site_desc(self) -> str:
        return "Foetus.org"
