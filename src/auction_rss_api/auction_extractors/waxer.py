from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class Waxer(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "waxer.eu"

    @property
    def site_desc(self) -> str:
        return "Waxer"
