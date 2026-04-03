from models.auctionextractor_shopify import ShopifySearchExtractor


class RedEye(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "redeye.com.au"

    @property
    def site_desc(self) -> str:
        return "Red Eye Records"
