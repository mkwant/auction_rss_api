from fastapi import FastAPI

from src.app.middleware import AddNoIndex
from src.routers import redirect
from src.routers import rss

# TODO Add function to generate random User Agent
# TODO Documentation

# Instantiate FastApi
app = FastAPI(
    title='Auction to RSS',
    version='1.7.1'
)

# Add routers and middleware
app.include_router(rss.router)
app.include_router(redirect.router)
app.add_middleware(middleware_class=AddNoIndex)
