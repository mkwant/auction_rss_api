from auction_extractors.marktplaats import Marktplaats


class TweedeHands(Marktplaats):
    DOMAIN: str = '2dehands.be'

    @property
    def site_desc(self) -> str:
        return '2dehands.be'

    @property
    def search_link(self) -> str:
        return f'https://www.{self.DOMAIN}/q/{self.search_term}'
