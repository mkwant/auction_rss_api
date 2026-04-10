from fastapi import APIRouter
from httpx import __version__
from starlette.responses import JSONResponse

from auction_rss_api.routers.logger import LoggedRoute

router = APIRouter(
    route_class=LoggedRoute,
    default_response_class=JSONResponse,
    tags=['Health']
)


@router.get(path='/version')
def version() -> JSONResponse:
    return JSONResponse({'version': __version__})
