from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class RockaBuy(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "rockabuyrecords.co.uk"

    @property
    def site_desc(self) -> str:
        return "RockaBuy Records"
