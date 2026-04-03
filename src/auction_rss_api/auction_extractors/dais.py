from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class Dais(ShopifyExtractor):
    @property
    def site_desc(self) -> str:
        return "Dais"

    @property
    def domain(self):
        return 'daisrecords.com'
