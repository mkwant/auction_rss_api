from fastapi import APIRouter
from fastapi_rss import RSSResponse

from auction_rss_api.auction_extractors.amatterofconcrete import AMatterOfConcrete
from auction_rss_api.routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=RSSResponse,
    tags=['Other shops']
)

@router.get(path='/amatterofconcrete')
def amatterofconcrete_rss(search_term: str, available_only: bool = False) -> RSSResponse:
    site = AMatterOfConcrete(search_term=search_term, available_only=available_only)
    return site.search()
