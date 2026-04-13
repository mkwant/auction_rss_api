from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class AtlasRecords(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "atlasrecords.co.uk"

    @property
    def site_desc(self) -> str:
        return "AtlasRecords"
