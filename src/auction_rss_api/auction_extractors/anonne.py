from auction_rss_api.models.auctionextractor_greedbag import GreedbagExtractor


class Anonne(GreedbagExtractor):
    @property
    def site_name(self) -> str:
        return 'anonne'
