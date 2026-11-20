from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class BenDoxBookshop(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "bendox.cz/en"

    @property
    def site_desc(self) -> str:
        return "Bendox Bookshop"
