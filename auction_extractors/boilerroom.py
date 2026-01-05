from models.auctionextractor_shopify import ShopifySearchExtractor


class BoilerRoom(ShopifySearchExtractor):
    @property
    def domain(self) -> str:
        return "boilerroomrecords.co.uk"

    @property
    def site_desc(self) -> str:
        return "Boiler Room Records"
