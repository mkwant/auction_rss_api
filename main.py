from fastapi import FastAPI

from app.middleware import AddNoIndex
from routers import redirect, rss

# TODO Add function to generate random User Agent
# TODO Documentation
# TODO Don't translate error item

# Instantiate FastApi
app = FastAPI(
    title='Auction to RSS',
    version='1.7.3'
)

# Add routers and middleware
app.include_router(rss.router)
app.include_router(redirect.router)
app.add_middleware(middleware_class=AddNoIndex)
