from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class CashensGap(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "cashensgap.com"

    @property
    def site_desc(self) -> str:
        return "Cashens Gap"
