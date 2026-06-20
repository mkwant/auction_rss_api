from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class NewBuryComics(ShopifyExtractor):
    @property
    def domain(self) -> str:
        return "newburycomics.com/collections/exclusive-vinyl"

    @property
    def site_desc(self) -> str:
        return "NewBuryComics"
