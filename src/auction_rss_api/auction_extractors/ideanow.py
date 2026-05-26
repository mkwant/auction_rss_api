from models.auctionextractor_shopify import ShopifySearchExtractor


class IdeaNow(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "ideanow.online"

    @property
    def site_desc(self) -> str:
        return "IdeaNow"
