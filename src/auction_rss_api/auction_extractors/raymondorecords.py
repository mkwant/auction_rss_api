from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class RaymondoRecords(ShopifyExtractor):

    @property
    def domain(self) -> str:
        return "raymondorecords.com"

    @property
    def site_desc(self) -> str:
        if self.collection:
            return f"RaymondoRecords (collection '{self.collection}')"
        return "RaymondoRecords"
