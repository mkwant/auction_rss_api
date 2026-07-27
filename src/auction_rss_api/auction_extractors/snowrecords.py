from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class SnowRecords(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "www.snowrecords.com"

    @property
    def site_desc(self) -> str:
        return "SnowRecords"
