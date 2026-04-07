from models.auctionextractor_shopify import ShopifyExtractor, ShopifySearchExtractor


class AtlasRecords(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "atlasrecords.co.uk"

    @property
    def site_desc(self) -> str:
        return "AtlasRecords"
