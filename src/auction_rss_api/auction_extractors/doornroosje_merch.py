from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class DoornroosjeMerch(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "merch.doornroosje.nl"

    @property
    def site_desc(self) -> str:
        return "DoornroosjeMerch"
