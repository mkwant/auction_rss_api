import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import AnyUrl

from auction_rss_api import __version__
from auction_rss_api.models.xmlresponse import XMLResponse
from auction_rss_api.routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    tags=['Tools']
)


@router.get(path="/proxy")
def proxy_rss(url: AnyUrl) -> XMLResponse:
    """Takes an existing RSS feed and passed it through as is."""
    r = httpx.get(str(url))
    r.raise_for_status()
    return XMLResponse(r.text)


@router.get(path='/version')
def version() -> JSONResponse:
    return JSONResponse({'version': __version__})
