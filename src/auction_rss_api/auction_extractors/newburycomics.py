from auction_rss_api.models.auctionextractor_shopify import ShopifyExtractor


class NewBuryComics(ShopifyExtractor):
    collection: str = "exclusive-vinyl"

    @property
    def domain(self) -> str:
        return "newburycomics.com"

    @property
    def site_desc(self) -> str:
        return "NewBuryComics"
