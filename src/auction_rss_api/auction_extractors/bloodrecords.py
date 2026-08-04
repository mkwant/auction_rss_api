from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class BloodRecords(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "blood-records.co.uk"

    @property
    def site_desc(self) -> str:
        if self.collection:
            return f"Blood Records (collection: '{self.collection}')"
        return "Blood Records"
