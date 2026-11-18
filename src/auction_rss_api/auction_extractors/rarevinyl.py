from urllib.parse import quote_plus

from auction_rss_api.models.auctionextractor_shopify import ShopifySearchExtractor


class RareVinyl(ShopifySearchExtractor):
    @property
    def search_link(self) -> str:
        return f"https://{self.domain}/search?q={quote_plus(self.search_term)}&sort_by=created"

    @property
    def domain(self) -> str:
        return 'eu.rarevinyl.com'

    @property
    def site_desc(self) -> str:
        return 'RareVinyl'
