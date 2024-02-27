from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class AddNoIndex(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["x-robots-tag"] = 'noindex, nofollow'

        return response
