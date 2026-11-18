from auction_rss_api.models.auctionextractor_shopify import ShopifySearchBrowserExtractor


class BoilerRoom(ShopifySearchBrowserExtractor):
    @property
    def domain(self) -> str:
        return "boilerroomrecords.co.uk"

    @property
    def site_desc(self) -> str:
        return "Boiler Room Records"
