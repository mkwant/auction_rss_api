from fastapi import FastAPI

from app.middleware import AddNoIndex
from routers import redirect, rss

# TODO Add function to generate random User Agent
# TODO Documentation

# Instantiate FastApi
app = FastAPI(
    title='AuctionRSS',
    version='1.9.8',
    description='This API returns RSS feeds for the search results of (mostly) auction sites.'
)

# Add routers and middleware
app.include_router(rss.router)
app.include_router(redirect.router)
app.add_middleware(middleware_class=AddNoIndex)
