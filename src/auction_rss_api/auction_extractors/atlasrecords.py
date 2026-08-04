from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor, ShopifySearchExtractor


class AtlasRecords(ShopifyExtractor):

    @property
    def domain(self) -> str:
        return "atlasrecords.co.uk"

    @property
    def site_desc(self) -> str:
        if self.collection:
            return f"AtlasRecords (collection '{self.collection}')"
        return "AtlasRecords"
