from models.auctionextractor_shopify import ShopifySearchExtractor


class Rockaway(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return 'rockaway.com'

    @property
    def site_desc(self) -> str:
        return 'Rockaway'
