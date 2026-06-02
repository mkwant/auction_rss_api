from fastapi import APIRouter
from fastapi_rss import RSSResponse

from auction_rss_api.auction_extractors.amatterofconcrete import AMatterOfConcrete
from auction_rss_api.auction_extractors.beeldengeluid import BeeldEnGeluid
from auction_rss_api.auction_extractors.bowiewonderworld import BowieWonderWorld
from auction_rss_api.auction_extractors.illustrateddbdiscography import IllustratedDBDiscography
from auction_rss_api.auction_extractors.indebuurt import InDeBuurt
from auction_rss_api.auction_extractors.justanothercollection import JustAnotherCollection
from auction_rss_api.auction_extractors.redhandfiles import RedHandFiles
from auction_rss_api.routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=RSSResponse,
    tags=['Other sites']
)


@router.get(path='/amatterofconcrete')
def amatterofconcrete_rss(search_term: str, available_only: bool = False) -> RSSResponse:
    site = AMatterOfConcrete(search_term=search_term, available_only=available_only)
    return site.search()


@router.get(path='/beeldengeluid')
def beeldengeluid_rss(search_term: str) -> RSSResponse:
    site = BeeldEnGeluid(search_term=search_term)
    return site.search()


@router.get(path='/bowiewonderworld')
def bowiewonderworld_rss() -> RSSResponse:
    site = BowieWonderWorld()
    return site.search()


@router.get(path='/illustrateddbdiscography')
def illustrateddbdiscography_rss() -> RSSResponse:
    site = IllustratedDBDiscography()
    return site.search()


@router.get(path='/indebuurt')
def indebuurt_rss(city: str) -> RSSResponse:
    site = InDeBuurt(search_term=city)
    return site.search()


@router.get(path='/justanothercollection')
def justanothercollection_rss() -> RSSResponse:
    site = JustAnotherCollection()
    return site.search()


@router.get(path='/redhandfiles')
def redhandfiles_rss() -> RSSResponse:
    site = RedHandFiles()
    return site.search()
