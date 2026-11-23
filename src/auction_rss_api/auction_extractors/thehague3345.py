from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class TheHague3345(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "3345.nl/nl"

    @property
    def site_desc(self) -> str:
        return "3345"
