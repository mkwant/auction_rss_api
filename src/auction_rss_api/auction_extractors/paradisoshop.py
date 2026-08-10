from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class ParadisoShop(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "merch.paradiso.nl"

    @property
    def site_desc(self) -> str:
        return "ParadisoShop"
