import logging
from pathlib import Path

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from app.logs import setup_logging
from app.middleware import AddNoIndex
from app.settings import settings
from routers import redirect, rss

# TODO Add function to generate random User Agent
# TODO Documentation

# Setting up logging
setup_logging(
    log_location=Path('/logs/auction_rss_api.log'),
    log_level=settings.LOG_LEVEL
)
logger = logging.getLogger(__name__)

# Instantiate FastApi
app = FastAPI(
    title='AuctionRSS',
    version='1.14.20',
    description='This API returns RSS feeds for the search results of (mostly) auction sites.'
)

logger.info('Starting application...')

# Add routers and middleware
app.include_router(rss.router)
app.include_router(redirect.router)
app.add_middleware(middleware_class=AddNoIndex)
app.add_middleware(middleware_class=CorrelationIdMiddleware)
