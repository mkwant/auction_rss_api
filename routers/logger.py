"""Custom route class that logs all requests plus the timing."""
import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

logger = logging.getLogger(__name__)


class LoggedRoute(APIRoute):
    """This route class can be used in an APIRouter route_class.
    It logs all incoming requests as well as the duration."""
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            logger.info(f'{request.client.host} {request.method} {request.url.path}?{request.query_params}')
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            logger.info(f"Finished in {duration:.2f} seconds")
            return response

        return custom_route_handler
