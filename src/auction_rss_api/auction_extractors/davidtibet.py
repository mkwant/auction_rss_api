from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class DavidTibet(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return 'davidtibet.com'

    @property
    def site_desc(self) -> str:
        return "DavidTibet"
