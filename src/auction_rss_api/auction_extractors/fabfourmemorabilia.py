from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class FabFourMemorabilia(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "fabfourmemorabilia.co.uk"

    @property
    def site_desc(self) -> str:
        return "FabFourMemorabilia"
