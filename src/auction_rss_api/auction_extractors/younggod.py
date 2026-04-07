from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class YoungGod(ShopifyExtractor):
    @property
    def site_desc(self) -> str:
        return "Young God Records"

    @property
    def domain(self):
        return 'younggodrecords.com'
