from fastapi import APIRouter
from fastapi_rss import RSSResponse

from auction_extractors.doornroosje import Doornroosje
from auction_extractors.effenaar import Effenaar
from auction_extractors.melkweg import Melkweg
from auction_extractors.paradiso import Paradiso
from auction_extractors.tilburg013 import Tilburg013
from auction_extractors.tivolivredenburg import TivoliVredenburg
from routers.logger import LoggedRoute

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


@router.get(path='/effenaar')
def effenaar_rss() -> RSSResponse:
    site = Effenaar()
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
