from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class WaxPoetics(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return 'waxpoetics.com'

    @property
    def site_desc(self) -> str:
        return "WaxPoetics"
