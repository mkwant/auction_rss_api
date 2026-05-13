from fastapi import APIRouter
from fastapi_rss import RSSResponse

from auction_rss_api.auction_extractors.doornroosje import Doornroosje
from auction_rss_api.auction_extractors.doornroosje_pas import DoornroosjePas
from auction_rss_api.auction_extractors.doornroosje_resale import DoornroosjeResale
from auction_rss_api.auction_extractors.effenaar import Effenaar
from auction_rss_api.auction_extractors.ekko import Ekko
from auction_rss_api.auction_extractors.melkweg import Melkweg
from auction_rss_api.auction_extractors.paradiso import Paradiso
from auction_rss_api.auction_extractors.tilburg013 import Tilburg013
from auction_rss_api.auction_extractors.tivoli_presale import TivoliPresale
from auction_rss_api.auction_extractors.tivolivredenburg import TivoliVredenburg
from auction_rss_api.auction_extractors.vera import Vera
from auction_rss_api.routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=RSSResponse,
    tags=['Concert venues']
)


@router.get(path='/013')
def tilburg013_rss() -> RSSResponse:
    site = Tilburg013()
    return site.search()


@router.get(path='/doornroosje')
def doornroosje_rss(location: str | None = None) -> RSSResponse:
    site = Doornroosje(search_term=location)
    return site.search()


@router.get(path='/doornroosje_pas')
def doornroosjepas_rss() -> RSSResponse:
    site = DoornroosjePas()
    return site.search()


@router.get(path='/doornroosje_resale')
def doornroosjeresale_rss(available_only: bool = False) -> RSSResponse:
    site = DoornroosjeResale(available_only=available_only)
    return site.search()


@router.get(path='/effenaar')
def effenaar_rss() -> RSSResponse:
    site = Effenaar()
    return site.search()


@router.get(path='/ekko')
def ekko_rss() -> RSSResponse:
    site = Ekko()
    return site.search()


@router.get(path='/melkweg')
def melkweg_rss() -> RSSResponse:
    site = Melkweg()
    return site.search()


@router.get(path='/paradiso')
def paradiso_rss() -> RSSResponse:
    site = Paradiso()
    return site.search()


@router.get(path='/tivolivredenburg')
def tivolivredenburg_rss() -> RSSResponse:
    site = TivoliVredenburg()
    return site.search()


@router.get(path='/tivolivredenburg_presale')
def tivolivredenburgpresale_rss(presale_id: str) -> RSSResponse:
    site = TivoliPresale(search_term=presale_id)
    return site.search()


@router.get(path='/vera')
def vera_rss() -> RSSResponse:
    site = Vera()
    return site.search()
