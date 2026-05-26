from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class IdeaNow(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "ideanow.online"

    @property
    def site_desc(self) -> str:
        return "IdeaNow"
