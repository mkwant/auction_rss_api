from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class DavidTibet(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return 'www.davidtibet.com'

    @property
    def site_desc(self) -> str:
        return "DavidTibet"
