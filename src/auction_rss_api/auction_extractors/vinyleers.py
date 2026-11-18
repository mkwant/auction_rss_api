from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class Vinyleers(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "vinyleers.com"

    @property
    def site_desc(self) -> str:
        return "Vinyleers"
