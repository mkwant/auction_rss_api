from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class BadWorld(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "bad-world.co.uk"

    @property
    def site_desc(self) -> str:
        return "Bad World Records"
