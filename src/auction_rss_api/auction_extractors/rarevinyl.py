from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class RareVinyl(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return 'eu.rarevinyl.com'

    @property
    def site_desc(self) -> str:
        return 'RareVinyl'
