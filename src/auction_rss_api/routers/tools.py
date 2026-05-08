import httpx
from fastapi import APIRouter
from fastapi_rss import RSSResponse
from starlette.responses import Response

from auction_rss_api.routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=RSSResponse,
    tags=['Tools']
)


class XMLResponse(Response):
    """
    A subclass of starlette.responses.Response which will set the content
    to an RSS XML document.
    """
    media_type = 'application/xml'
    charset = 'utf-8'


@router.get(path="/proxy")
def proxy_rss(url: str) -> XMLResponse:
    """Takes an existing RSS feed and passed it through as is."""
    r = httpx.get(url)
    r.raise_for_status()
    return XMLResponse(r.text)
