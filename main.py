from fastapi import FastAPI, Request

from routers import redirect
from routers import rss

# TODO Add function to generate random User Agent
# TODO Move code to src subdir
# TODO Import middleware and redirect
# TODO Documentation

app = FastAPI(
    title='Auction to RSS',
    version='1.7.0'
)


@app.middleware("http")
async def add_noindex(request: Request, call_next):
    """Adding x-robots-tag to response headers to exclude from search engines."""
    response = await call_next(request)
    response.headers["x-robots-tag"] = 'noindex, nofollow'
    return response


app.include_router(rss.router)
app.include_router(redirect.router)
